/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

// This is a workaround for PDF.js 2.7.x and Webpack 4.x compatibility
// 2.7.x series switched to modern JS ES2018 and we are still using Vue Cli 4 with
// only support for Webpack 4. This workaround should be removed when Vue Cli is upgraded to 5

// import pdfjsLib from "pdfjs-dist/webpack";
var pdfjsLib = require("pdfjs-dist/build/pdf.js");
var PdfjsWorker = require("worker-loader?esModule=false!pdfjs-dist/build/pdf.worker.js");

if (typeof window !== "undefined" && "Worker" in window) {
  pdfjsLib.GlobalWorkerOptions.workerPort = new PdfjsWorker();
}

// pdfjsLib.disableWorker = true;
window.URL = window.URL || window.webkitURL;

export const createThumbFromFile = function (file) {
  let objectURL = window.URL.createObjectURL(file);
  return createThumbFromUrl(objectURL);
};

export const createThumbFromUrl = function (url) {
  return new Promise((resolve, reject) => {
    let loadingTask = pdfjsLib.getDocument(url);
    loadingTask.promise
      .then(function (pdf) {
        pdf
          .getPage(1)
          .then(function (page) {
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");

            let viewport = page.getViewport({ scale: 0.5 });

            canvas.height = viewport.height;
            canvas.width = viewport.width;

            let render = page.render({
              canvasContext: context,
              viewport: viewport,
            });

            render.promise.then(function () {
              resolve(canvas.toDataURL());
            });
          })
          .catch(function () {
            reject(
              "pdf thumb error: could not open page 1 of document " +
                url +
                ". Not a pdf ?"
            );
          });
      })
      .catch(function () {
        reject(
          "pdf thumb error: could not find or open document " +
            url +
            ". Not a pdf ?"
        );
      });
  });
};
