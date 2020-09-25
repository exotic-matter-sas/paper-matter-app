/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

// Use `vue-cli-service inspect` to display output webpack.config.js
const BundleTracker = require("webpack-bundle-tracker");
const webpack = require("webpack");

module.exports = {
  publicPath: process.env.NODE_ENV === "production" ? "/assets/" : "/local/",
  outputDir: "./dist/",
  lintOnSave: "error",

  css: {
    // Needed to render css bundle in Django base template when in development
    // Unfortunately it disable css hot reloading
    extract: true,
    loaderOptions: {
      sass: {
        prependData: `@import "@/styles/_variables.scss";`,
      },
    },
  },

  productionSourceMap: false,

  chainWebpack: (config) => {
    config
      .plugin("skip-moment-locale")
      .use(webpack.ContextReplacementPlugin, [/moment[/\\]locale$/, /en|fr/]);

    config.entry("common").add("@/styles/common.scss");
    config.entry("common_logged_in").add("@/styles/common_logged_in.scss");
    config.entry("common_logged_out").add("@/styles/common_logged_out.scss");
    config.entry("account").add("@/styles/account.scss");
    config.entry("share_doc").add("@/styles/share_doc.scss");
    config
      .entry("supported_browsers")
      .add("@/standalone_scripts/supportedBrowsers");

    // Built app broken if omitted
    config.optimization.splitChunks(false);

    config
      .plugin("BundleTracker")
      .use(BundleTracker, [{ filename: "./webpack-stats.json" }]);

    config.resolve.alias.set("__STATIC__", "static");

    config.devServer
      .public("http://127.0.0.1:8080")
      .host("127.0.0.1")
      .port(8080)
      .hotOnly(true)
      .watchOptions({ ignored: /node_modules/ })
      .https(false)
      .headers({
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Origin": ["*"],
      });

    config.module
      .rule("eslint")
      .use("eslint-loader")
      .tap((options) => {
        options.failOnWarning = true;
        return options;
      });

    config.module
      .rule("i18n")
      .resourceQuery(/blockType=i18n/)
      .type("javascript/auto")
      .use("i18n")
      .loader("@intlify/vue-i18n-loader")
      .end()
      .use("yaml")
      .loader("yaml-loader")
      .end();
  },

  pluginOptions: {
    i18n: {
      locale: "en",
      fallbackLocale: "en",
      localeDir: "locales",
      enableInSFC: true,
    },
  },
};
