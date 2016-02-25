// Grunt software build task definitions.

module.exports = function(grunt) {
  'use strict';

  var fs = require('fs');
  var repodonostorageRequireJSOptions = require('./config');

  grunt.initConfig({
    //pkg: grunt.file.readJSON('../package.json'),

    karma: {
      test: {
        configFile: 'karma.conf.js'
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-requirejs');
  grunt.loadNpmTasks('grunt-karma');
  grunt.registerTask('test', ['karma:test']);

}
