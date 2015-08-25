
var AppDispatcher = require('../dispatcher/AppDispatcher');
var objectAssign = require('object-assign');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');

var APPCHANGE_EVENT = "APPCHANGE";

var _t = i18n.t;

var AppStore = objectAssign({}, EventEmitter.prototype, {
  addChangeListener: function(cb){
    this.on(APPCHANGE_EVENT, cb);
  },
  removeChangeListener: function(cb){
    this.removeListener(APPCHANGE_EVENT, cb);
  },
  getState: function(){
    return {t: _t};
  },
});

AppDispatcher.register(function(payload){
  var action = payload.action;
  switch(action){
    case AppConstants.actions.CHANGE_LANGUAGE:
    	_t = payload.response;
    	AppStore.emit(APPCHANGE_EVENT);
    	break;
    default:
      return true;
  }
});

module.exports = AppStore;