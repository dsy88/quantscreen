var AppDispatcher = require('./dispatcher/AppDispatcher');
var AppConstants = require('./constants/AppConstants');
var _pendingRequests = {};

var abortPendingRequests = function (key) {
  if (_pendingRequests[key]) {
    _pendingRequests[key]._callback = function(){};
    _pendingRequests[key].abort();
    _pendingRequests[key] = null;
  }
};

var dispatch = function (action, state) {
  var payload = {action: action, state: state};
  AppDispatcher.dispatch(payload);
};

var handleSuccess = function () {
  dispatch(AppConstants.AJAX.AJAX_REQUEST, AppConstants.AJAX.AJAX_SUCCEED);
};

var handleFail = function (request, error) {
  dispatch(AppConstants.AJAX.AJAX_REQUEST, AppConstants.AJAX.AJAX_FAILED);
};

var helper = {
  request: function(action, url, params, post, dataType, callback) {
    abortPendingRequests(action);
    dispatch(AppConstants.AJAX.AJAX_REQUEST, AppConstants.AJAX.AJAX_PENDING);
    if (post == true) {
      _pendingRequests[action] = $.post(url, params, function(data){
        handleSuccess();
        callback(data);
      }, dataType).fail(handleFail);
    } else {
      _pendingRequests[action] = $.get(url, params, function(data){
        handleSuccess();
        callback(data);
      }, dataType).fail(handleFail);
    }
  }
};

module.exports = helper;