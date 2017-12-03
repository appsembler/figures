
// ./node_modules/.bin/webpack --config webpack.config.js --watch

// 'use strict';

//var path = require("path")
const path = require('path');

var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

console.log("__dirname = "+__dirname);

module.exports = {
  context: __dirname,

  entry: './assets/js/index.js', // entry point of our app. assets/js/index.js should require other js modules and dependencies it needs

  output: {
      path: path.resolve('./edx_figures/static/edx_figures_bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './edx_figures/webpack-stats.json'}),
  ],

  module: {
    loaders: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader'}, // to transform JSX into JS
    ],
  },

  resolve: {
    extensions: ['.js', '.jsx']
  }
}


