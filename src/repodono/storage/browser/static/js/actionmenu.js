define([
  'jquery',
  'underscore',
], function($, _) {
  'use strict';

  var ActionMenu = function(menu) {
    var result = {};
    result['open'] = ['', '', menu.model.attributes.viewURL, 'Open'];
    if (menu.model.attributes.portal_type === "document") {
      result['download'] = ['', '', menu.model.attributes.viewURL, 'Download'];
    }
    return result;
  };

  return ActionMenu;
});
