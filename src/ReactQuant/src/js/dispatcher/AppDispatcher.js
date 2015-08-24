var Dispatcher = require('flux').Dispatcher;
var AppDispatcher = new Dispatcher();

AppDispatcher.handleAction = function(payload){
  this.dispatcher(payload);
};

module.exports = AppDispatcher;