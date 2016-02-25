define([
  'jquery',
  'underscore',
  'expect',
  'pat-registry',
  'mockup-patterns-structure',
  'mockup-patterns-structure-url/js/models/result',
  'repodonostorage-url/js/actionmenu',
], function($, _, expect, registry, Structure, Result, ActionMenu) {
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
});
