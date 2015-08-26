
var AppDispatcher = require('../dispatcher/AppDispatcher');
var objectAssign = require('object-assign');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');

var PEGRANKCHANGE_EVENT = "PEGRANKCHANGE";

var _colunms = [];

AppConstants.RANK.PEG_COLUMNS.map(function(name) {
  _colunms.push('colunms.' + name);
});

var _top = {};

var _currentPage = -1;
var _total = -1;

var PEGRankStore = objectAssign({}, EventEmitter.prototype, {
  addChangeListener: function(cb){
    this.on(PEGRANKCHANGE_EVENT, cb);
  },
  removeChangeListener: function(cb){
    this.removeListener(APPCHANGE_EVENT, cb);
  },
  getState: function(){
    return {colunms: _colunms,
            top: _top};
  },
});

AppDispatcher.register(function(payload){
  var action = payload.action;
  switch(action){
    case AppConstants.ACTIONS.UPDATE_PEGRANK:
      var response = payload.response;
      if (response.status == "OK") {
        _top[response.page] = response.data;
        _total = response.total;
        _currentPage = response.page;
        PEGRankStore.emit(PEGRANKCHANGE_EVENT); 
      }
      break;
    default:
      return true;
  }
});

module.exports = PEGRankStore;
