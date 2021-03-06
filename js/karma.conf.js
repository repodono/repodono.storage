module.exports = function(config) {
  config.set({

    // base path, that will be used to resolve files and exclude
    basePath: './',

    // frameworks to use
    frameworks: ['mocha', 'chai'],

    // list of files / patterns to load in the browser
    files: [

      /*
      * include initial framework (mocha and requirejs) with html5
      * shims/shams/polyfills
      */
      'node_modules/mocha/mocha.js',
      'node_modules/karma-mocha/lib/adapter.js',
      'node_modules/requirejs/require.js',
      'node_modules/karma-requirejs/lib/adapter.js',

      /*
      * include requirejs configuration
      */
      '../src/mockup/mockup/js/config.js',
      'config.js',

      'tests/config.js',

      /* provide but not include */
      {pattern: 'tests/**/*.js', included: false},
      {pattern: 'bower_components/**/*.js', included: false},
      {pattern: 'patterns/**/*', included: false},
      {pattern: 'js/**/*', included: false},
      {pattern: 'lib/**/*', included: false},
      {pattern: 'src/repodono/storage/browser/static/js/**/*', included: false},
      {pattern: 'src/repodono/storage/browser/static/templates/**/*', included: false},
    ],

    // list of files to exclude
    exclude: [
    ],

    // test results reporter to use
    reporters: ['dots', 'progress', 'spec'],

    // web server port
    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // level of logging
    logLevel: config.LOG_INFO,

    // Start these browsers
    browsers: ['PhantomJS'],

    // If browser does not capture in given timeout [ms], kill it
    captureTimeout: 60000,

    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: true,

    plugins: [
      'karma-mocha',
      'karma-chai',
      'karma-coverage',
      'karma-requirejs',
      'karma-sauce-launcher',
      'karma-chrome-launcher',
      'karma-phantomjs-launcher',
      'karma-junit-reporter',
      'karma-spec-reporter'
    ]


  });
};
