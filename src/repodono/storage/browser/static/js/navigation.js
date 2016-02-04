define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {
  var Navigation = Backbone.Model.extend({
    initialize: function(options) {
      this.options = options;
      this.app = options.app;
      this.model = options.model;
    },
    openClicked: function(e) {
      return true;
    }
  });
  return Navigation;
});
