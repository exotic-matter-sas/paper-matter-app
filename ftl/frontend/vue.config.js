/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

// Use `vue-cli-service inspect` to display output webpack.config.js
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  publicPath: process.env.NODE_ENV === 'production' ? "/assets/" : "/local/",
  outputDir: './dist/',
  lintOnSave: 'error',
  css: {
    // Needed to render css bundle in Django base template when in development
    // Unfortunately it disable css hot reloading
    extract: true,
    loaderOptions: {
      sass: {
        prependData: `@import "@/styles/customBootstrap.scss";`
      }
    }
  },

  chainWebpack: config => {

    config.entry('app')
      .add('@/styles/customBootstrap.scss');

    // Built app broken if omitted
    config.optimization
      .splitChunks(false);

    config.plugin('BundleTracker')
      .use(BundleTracker, [{filename: './webpack-stats.json'}]);

    config.resolve.alias
      .set('__STATIC__', 'static');

    config.devServer
      .public('http://127.0.0.1:8080')
      .host('127.0.0.1')
      .port(8080)
      .hotOnly(true)
      .watchOptions({poll: 2500})
      .https(false)
      .headers({
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Origin": ["*"]
      });

    config.module
      .rule('eslint')
      .use('eslint-loader')
      .tap(options => {
        options.failOnWarning = true;
        return options;
      });
  }
};
