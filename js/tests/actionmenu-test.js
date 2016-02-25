define([
  'jquery',
  'underscore',
  'expect',
  'pat-registry',
  'mockup-patterns-structure',
  'mockup-patterns-structure-url/js/models/result',
  'mockup-patterns-structure-url/js/views/app',
  'mockup-patterns-structure-url/js/views/actionmenu',
  'repodonostorage-url/js/actionmenu',
], function($, _, expect, registry, Structure, Result, AppView, ActionMenuView,
            ActionMenu) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

  describe('Action menu test', function() {
    beforeEach(function() {
    });

    afterEach(function() {
    });

    it('Document type', function() {
      var dummy = {
        model: {
          attributes: {
            viewURL: 'http://localhost/test',
            portal_type: 'document'
          }
        }
      };
      var menu = ActionMenu(dummy);
      expect(_.size(menu)).to.equal(2);
      expect(menu.open).to.eql(
        ["", "", "http://localhost/test", "Open"]);
      expect(menu.download).to.eql(
        ["", "", "http://localhost/test", "Download"]);
    });

    it('Folder type (not document)', function() {
      var dummy = {
        model: {
          attributes: {
            viewURL: 'http://localhost/test',
            portal_type: 'folder'
          }
        }
      };
      var menu = ActionMenu(dummy);
      expect(_.size(menu)).to.equal(1);
      expect(menu.open).to.eql(
        ["", "", "http://localhost/test", "Open"]);
    });

  });

  describe('Action menu view test', function() {
    beforeEach(function() {
      this.app = new AppView({
        'buttons': [],
        'activeColumns': [],
        'availableColumns': [],
        'indexOptionsUrl': '',
        'setDefaultPageUrl': '',
        'collectionConstructor':
          'mockup-patterns-structure-url/js/collections/result',
      });
    });

    afterEach(function() {
    });

    it('Document type', function() {
      var model = new Result({
        viewURL: 'http://localhost/test',
        portal_type: 'document'
      });

      var view = new ActionMenuView({
        app: this.app,
        model: model,
        menuGenerator: 'repodonostorage-url/js/actionmenu'
      });

      var el = view.render().el;
      expect($('.open a', el).text()).to.eql('Open');
      expect($('.download a', el).text()).to.eql('Download');
    });

    it('Folder type (not document)', function() {
      var model = new Result({
        viewURL: 'http://localhost/test',
        portal_type: 'folder'
      });

      var view = new ActionMenuView({
        app: this.app,
        model: model,
        menuGenerator: 'repodonostorage-url/js/actionmenu'
      });

      var el = view.render().el;
      expect($('.open a', el).text()).to.eql('Open');
      expect($('.download a', el).length).to.be(0);
    });

  });

});
