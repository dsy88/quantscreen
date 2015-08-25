var AppDispatcher = require('./AppDispatcher');
var AppConstants = require('./AppConstants');
var _pendingRequests = {};

function abortPendingRequests(key) {
  if (_pendingRequests[key]) {
    _pendingRequests[key]._callback = function(){};
    _pendingRequests[key].abort();
    _pendingRequests[key] = null;
  }
};

function dispatch(action, state, params) {
  var payload = {action: action, state: state};
  if (params) {
  payload.queryParams = params;
  }
  AppDispatcher.handleAction(payload);
};

var helper = {
  request: function(action, url, params) {
  //abortPendingRequests(action);
  //dispatch(action, AppConstants.app.AJAX_PENDING, params);
  }
};

module.exports = helper;