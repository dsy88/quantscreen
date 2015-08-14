import pandas
import time
import xml.etree.ElementTree as ET
import requests
from collections import namedtuple
import datetime
from functools import partial
from six import iteritems
import pytz
import re
from collections import OrderedDict

Mapping = namedtuple('Mapping', ['conversion', 'source'])

def get_utc_from_exchange_time(naive):
    local = pytz.timezone('US/Eastern')
    local_dt = naive.replace(tzinfo=local)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def guarded_conversion(conversion, str_val):
    """
    Returns the result of applying the @conversion to @str_val
    """
    if str_val in (None, ""):
        return None
    return conversion(str_val)


def apply_mapping(mapping, row):
    """
    Returns the value of a @mapping for a given @row.

    i.e. the @mapping.source values are extracted from @row and fed
    into the @mapping.conversion method.
    """
    if isinstance(mapping.source, str):
        # Do a 'direct' conversion of one key from the source row.
        return guarded_conversion(mapping.conversion, row[mapping.source])
    if mapping.source is None:
        # For hardcoded values.
        # conversion method will return a constant value
        return mapping.conversion()
    else:
        # Assume we are using multiple source values.
        # Feed the source values in order prescribed by mapping.source
        # to mapping.conversion.
        return mapping.conversion(*[row[source] for source in mapping.source])


def _row_cb(mapping, row):
    """
    Returns the dict created from our @mapping of the source @row.

    Not intended to be used directly, but rather to be the base of another
    function that supplies the mapping value.
    """
    return {
        target: apply_mapping(mapping, row)
        for target, mapping
        in iteritems(mapping)
    }

def make_row_cb(mapping):
    """
    Returns a func that can be applied to a dict that returns the
    application of the @mapping, which results in a dict.
    """
    return partial(_row_cb, mapping)

def source_to_records(mappings,
                      source,
                      source_wrapper=None,
                      records_wrapper=None):
    if source_wrapper:
        source = source_wrapper(source)

    callback = make_row_cb(mappings)

    records = (callback(row) for row in source)

    if records_wrapper:
        records = records_wrapper(records)

    return records

def date_conversion(date_str, date_pattern='%m/%d/%Y', to_utc=True):
    """
    Convert date strings from TickData (or other source) into epoch values.

    Specify to_utc=False if the input date is already UTC (or is naive).
    """
    dt = datetime.datetime.strptime(date_str, date_pattern)
    if to_utc:
        dt = get_utc_from_exchange_time(dt)
    else:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt

def safe_int(str_val):
    """
    casts the @str_val to a float to handle the occassional
    decimal point in int fields from data providers.
    """
    f = float(str_val)
    i = int(f)
    return i

def get_treasury_date(dstring):
    return date_conversion(dstring.split("T")[0], date_pattern='%Y-%m-%d',
                           to_utc=False)


def get_treasury_rate(string_val):
    val = guarded_conversion(float, string_val)
    if val is not None:
        val = round(val / 100.0, 4)
    return val


_CURVE_MAPPINGS = {
    'tid': (safe_int, "Id"),
    'date': (get_treasury_date, "NEW_DATE"),
    '1month': (get_treasury_rate, "BC_1MONTH"),
    '3month': (get_treasury_rate, "BC_3MONTH"),
    '6month': (get_treasury_rate, "BC_6MONTH"),
    '1year': (get_treasury_rate, "BC_1YEAR"),
    '2year': (get_treasury_rate, "BC_2YEAR"),
    '3year': (get_treasury_rate, "BC_3YEAR"),
    '5year': (get_treasury_rate, "BC_5YEAR"),
    '7year': (get_treasury_rate, "BC_7YEAR"),
    '10year': (get_treasury_rate, "BC_10YEAR"),
    '20year': (get_treasury_rate, "BC_20YEAR"),
    '30year': (get_treasury_rate, "BC_30YEAR"),
}


def treasury_mappings(mappings):
    return {key: Mapping(*value)
            for key, value
            in iteritems(mappings)}

def get_localname(element):
    qtag = ET.QName(element.tag).text
    return re.match("(\{.*\})(.*)", qtag).group(2)

    
class iter_to_stream(object):
    """
    Exposes an iterable as an i/o stream
    """
    def __init__(self, iterable):
        self.buffered = ""
        self.iter = iter(iterable)

    def read(self, size):
        result = ""
        while size > 0:
            data = self.buffered or next(self.iter, None)
            self.buffered = ""
            if data is None:
                break
            size -= len(data)
            if size < 0:
                data, self.buffered = data[:size], data[size:]
            result += data
        return result
      
def get_treasury_source():
    url = """\
http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData\
"""
    res = requests.get(url, stream=True)
    stream = iter_to_stream(res.text.splitlines())

    elements = ET.iterparse(stream, ('end', 'start-ns', 'end-ns'))

    namespaces = OrderedDict()
    properties_xpath = ['']

    def updated_namespaces():
        if '' in namespaces and 'm' in namespaces:
            properties_xpath[0] = "{%s}content/{%s}properties" % (
                namespaces[''], namespaces['m']
            )
        else:
            properties_xpath[0] = ''

    for event, element in elements:
        if event == 'end':
            tag = get_localname(element)
            if tag == "entry":
                properties = element.find(properties_xpath[0])
                datum = {get_localname(node): node.text
                         for node in properties if ET.iselement(node)}
                # clear the element after we've dealt with it:
                element.clear()
                yield datum

        elif event == 'start-ns':
            namespaces[element[0]] = element[1]
            updated_namespaces()

        elif event == 'end-ns':
            namespaces.popitem()
            updated_namespaces()



def get_treasury_data():
    mappings = treasury_mappings(_CURVE_MAPPINGS)
    source = get_treasury_source()
    return source_to_records(mappings, source)

if __name__ == "__main__":
  tr_data = {}
  current = time.time()
  for curve in get_treasury_data():
    tr_data[curve['date']] = curve
  
  curves = pandas.DataFrame(tr_data).T

  curves.to_csv('treasuries' + time.strftime("-%Y-%m-%d") +'.csv')
  print "Total Time", time.time() - current
