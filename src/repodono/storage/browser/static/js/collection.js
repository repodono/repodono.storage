define([
  'underscore',
  'backbone',
  'mockup-patterns-structure-url/js/models/result',
  'backbone.paginator'
], function(_, Backbone, Result) {
  'use strict';

  var ResultCollection = Backbone.Paginator.requestPager.extend({
    model: Result,
    initialize: function(models, options) {
      this.options = options;
      this.view = options.view;
      this.url = options.url;
      this.path = options.view.traverseSubpath || '/';

      Backbone.Paginator.requestPager.prototype.initialize.apply(this, [models, options]);
    },
    getCurrentPath: function() {
      return this.path;
    },
    setCurrentPath: function(path) {
      this.path = path;
    },
    pager: function() {
      this.trigger('pager');
      Backbone.Paginator.requestPager.prototype.pager.apply(this, []);
    },
    paginator_core: {
      // the type of the request (GET by default)
      type: 'GET',
      // the type of reply (jsonp by default)
      dataType: 'json',
      url: function() {
        return this.url + '/' + this.path;
      }
    },
    paginator_ui: {
      // the lowest page index your API allows to be accessed
      firstPage: 1,
      // which page should the paginator start from
      // (also, the actual page the paginator is on)
      currentPage: 1,
      // how many items per page should be shown
      perPage: 15
    },
    // server_api are query parameters passed directly (currently GET
    // parameters).  These are currently generated using following
    // functions.  Renamed to queryParams in Backbone.Paginator 2.0.
    server_api: {},
    parse: function (response, baseSortIdx) {
      if(baseSortIdx === undefined){
        baseSortIdx = 0;
      }
      this.totalRecords = response.total;
      var results = response.results;
      // XXX manually set sort order here since backbone will otherwise
      // do arbitrary sorting?
      _.each(results, function(item, idx) {
        item._sort = idx;
      });
      return results;
    },
    comparator: '_sort'
  });

  return ResultCollection;
});
