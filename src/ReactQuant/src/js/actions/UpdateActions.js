var AppDispatcher = require('../dispatcher/AppDispatcher');
var AppConstants = require('../constants/AppConstants');
var AppHelper = require('../AppHelper');

var changeLanuage = function(lang) {
  i18n.init({lng: lang}, function(err, t) {
  	AppDispatcher.dispatch({action: AppConstants.ACTIONS.CHANGE_LANGUAGE, response:t});
  });
};

var updatePEGTop = function(response) {
  AppDispatcher.dispatch({action: AppConstants.ACTIONS.UPDATE_PEGRANK, response: response});
};

var UpdateActions = {
  updatePEGRank: function() {
    AppHelper.request(AppConstants.ACTIONS.UPDATE_PEGRANK,
                      "api/rank/pegtop",
                      null,
                      false,
                      "json",
                      updatePEGTop);
  },
  updateDividendRank: function() {

  },
  updateLanguage: function(lang) {
    changeLanuage(lang);
  }
};

module.exports = UpdateActions;