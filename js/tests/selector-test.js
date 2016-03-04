define([
  'jquery',
  'underscore',
  'expect',
  'sinon',

  'pat-registry',
  'mockup-patterns-structure',

  'repodonostorage-url/js/selector',
  'repodonostorage-url/js/collection',
], function($, _, expect, sinon,
            registry, Structure,
            SelectorView) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

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

  describe('Core functionality tests', function() {
    beforeEach(function() {
    });

    afterEach(function() {
    });

    it('basic rendering', function() {
      // id to name first to aid initial lookup
      // present as name to data-id to aid navigation
      var data = {
        'branches': [
          ['master', '0abcd123'],
          ['feature', '1cdef678'],
        ],
        'tags': [
          ['0.1', '2aceb987'],
        ],
      };
      var view = new SelectorView({
        branches: data.branches,
        heading: 'branch',
        label: 'master',
      });
      var $el = view.render().$el;
      var $menu = $('.dropdown-menu', $el);
      expect($('button', $el).text().trim()).to.eql('branch: master');
      expect($('li', $menu).length).to.equal(2);
      expect($('li a', $menu).eq(0).text()).to.eql('master');
      expect($('li a', $menu).eq(0).data()['path']).to.eql('/0abcd123');
      expect($('li a', $menu).eq(1).text()).to.eql('feature');
      expect($('li a', $menu).eq(1).data()['path']).to.eql('/1cdef678');
    });

  });

});
