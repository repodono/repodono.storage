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

      this.server = sinon.fakeServer.create();
      this.server.autoRespond = true;
      this.server.respondWith('GET', /json/, function (xhr, id) {
        var commit = '0';
        var targetPath = traverseSubpath || '/' + commit;

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

  });

});
