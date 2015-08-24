var AppDispatcher = require('../dispatcher/AppDispatcher');
var AppConstants = require('../constants/AppConstants');

var changeLanuage = function(lang) {
  i18n.init({lng: lang}, function(err, t) {
  	AppDispatcher.dispatch({action: AppConstants.actions.CHANGE_LANGUAGE, response:t});
  });
};

var UpdateActions = {
  updatePEGRank: function() {

  },
  updateDividendRank: function() {

  },
  updateLanguage: function(lang) {
    changeLanuage(lang);
  }
};

module.exports = UpdateActions;