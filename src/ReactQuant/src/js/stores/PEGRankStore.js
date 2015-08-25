
var AppDispatcher = require('../dispatcher/AppDispatcher');
var objectAssign = require('object-assign');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');

var PEGRANKCHANGE_EVENT = "PEGRANKCHANGE";

var _columns = [];

var PEGRankStore = objectAssign({}, EventEmitter.prototype, {
  addChangeListener: function(cb){
    this.on(PEGRANKCHANGE_EVENT, cb);
  },
  removeChangeListener: function(cb){
    this.removeListener(APPCHANGE_EVENT, cb);
  },
  getState: function(){
    return {columns: _columns};
  },
});

AppDispatcher.register(function(payload){
  var action = payload.action;
  switch(action){
    case AppConstants.actions.UPDATE_PEGRANK:
      AppStore.emit(PEGRANKCHANGE_EVENT);
      break;
    default:
      return true;
  }
});

module.exports = PEGRankStore;
