define([
  'jquery',
  'underscore',
  'backbone',
  'text!repodonostorage-url/templates/selector.xml',
], function($, _, Backbone, SelectorTemplate) {
  'use strict';

  var SelectorView = Backbone.View.extend({
    tagName: 'span',
    className: 'btn-group input-group branch-selector',
    initialize: function(options) {
      this.collection = options.collection;
      this.branches = options.branches;
      this.label = options.label;
      this.heading = options.heading;
    },
    template: _.template(SelectorTemplate),
    render: function() {
      var self = this;
      self.$el.html(self.template(self));
      return this;
    },
  });

  return SelectorView;
});
