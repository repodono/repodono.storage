define([
  'jquery',
  'underscore',
  'expect',
  'sinon',

  'pat-registry',
  'mockup-patterns-structure',
  'mockup-patterns-structure-url/js/models/result',
  'mockup-patterns-structure-url/js/views/app',
  'mockup-patterns-structure-url/js/views/actionmenu',

  'repodonostorage-url/js/actionmenu',
  'repodonostorage-url/js/collection'
], function($, _, expect, sinon,
            registry, Structure, Result, AppView, ActionMenuView,
            ActionMenu) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  var history = {
    'pushState': function(data, title, url) {
      history.pushed = {
        data: data,
        title: title,
        url: url
      };
    }
  };

  var traverseSubpath = '';

  var initStructure = function(self) {
    var structure = {
      'vocabularyUrl': '/json',
      // dummy value.
      'indexOptionsUrl': '/tests/json/queryStringCriteria.json',
      'buttons': [],
      'activeColumns': ['ModificationDate', 'getObjSize'],
      'activeColumnsCookie': 'activeStorageColumns',
      'availableColumns': {
        'id': 'ID',
        'ModificationDate': 'LastModified',
        'getObjSize': 'Object Size',
      },
      'pushStateUrl': 'http://localhost:8081/view/{path}',
      'traverseView': true,
      'attributes': ['Title', 'getURL', 'viewURL', 'ModificationDate',
        'getObjSize', 'is_folderish', 'portal_type', 'id', 'UID', 'path'],
      'menuGenerator': 'repodonostorage-url/js/actionmenu',

      'collectionConstructor': 'repodonostorage-url/js/collection',
      'traverseSubpath': traverseSubpath
    };

    self.$el = $('<div class="pat-structure"></div>').attr(
      'data-pat-structure', JSON.stringify(structure)).appendTo('body');
    registry.scan(self.$el);
    self.clock.tick(1000);
  }

  describe('Custom collection test', function() {
    beforeEach(function() {
      this.clock = sinon.useFakeTimers();
      this.sandbox = sinon.sandbox.create();
      this.sandbox.stub(window, 'history', history);

      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;
      this.server.respondWith('GET', /json/, function (xhr, id) {
        traverseSubpath = xhr.url.substr(
          0, xhr.url.indexOf('?')).replace('/json/', '');
        var commit = '0';
        var targetPath = (traverseSubpath === '/' ?
          '/' + commit : traverseSubpath);

        var items = [{
          'Title': 'folder',
          'portal_type': 'folder',
        }, {
          'Title': 'file.txt',
          'portal_type': 'document',
        }];

        _.each(items, function(item) {
          item.path = targetPath + '/' + item.Title;
          item.id = item.path;
          item.UID = item.path;
          item.getURL = 'http://localhost:8081/view' + item.path;
          item.is_folderish = item.portal_type === 'folder';
        })

        xhr.respond(200, {'Content-Type': 'application/json'}, JSON.stringify({
          total: 2,
          results: items
        }));
      });

    });

    afterEach(function() {
      this.server.restore();
      this.sandbox.restore();
      this.clock.restore();
      this.$el.remove();

      $('body').html('');

      traverseSubpath = '';
    });

    it('basic rendering', function() {
      initStructure(this);

      expect($('.itemRow', this.$el).length).to.equal(2);
      var folder = $('.itemRow', this.$el).eq(0);
      var doc = $('.itemRow', this.$el).eq(1);

      expect($('.title a', folder).attr('href')).to.eql(
        'http://localhost:8081/view/0/folder')

      expect($('.open a', folder).text()).to.eql('Open');
      expect($('.download', folder).length).to.eql(0);

      expect($('.open a', doc).text()).to.eql('Open');
      expect($('.download a', doc).text()).to.eql('Download');

    });

    it('navigation', function() {
      initStructure(this);

      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/0/folder')
      $('.itemRow .title a', this.$el).eq(0).trigger('click');
      this.clock.tick(1000);

      expect(traverseSubpath).to.eql('/0/folder')
      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/0/folder/folder')
      $('.itemRow .title a', this.$el).eq(0).trigger('click');
      this.clock.tick(1000);

      expect(traverseSubpath).to.eql('/0/folder/folder')
      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/0/folder/folder/folder')
      $('.itemRow .title a', this.$el).eq(0).trigger('click');
      this.clock.tick(1000);

      expect(traverseSubpath).to.eql('/0/folder/folder/folder')
      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/0/folder/folder/folder/folder')

      // pop back up a couple steps via breadcrumbs
      var crumb1 = $('.fc-breadcrumbs a.crumb', this.$el).eq(1)
      crumb1.trigger('click');
      this.clock.tick(1000);
      expect(traverseSubpath).to.eql('/0/folder')
      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/0/folder/folder')
    });

    it('initialize with predefined traverseSubpath', function() {
      traverseSubpath = '/2/folder';
      initStructure(this);

      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/2/folder/folder')
      $('.itemRow .title a', this.$el).eq(0).trigger('click');
      this.clock.tick(1000);

      expect(traverseSubpath).to.eql('/2/folder/folder')
      expect($('.itemRow .title a', this.$el).attr('href')).to.eql(
        'http://localhost:8081/view/2/folder/folder/folder')

    });

  });

});
