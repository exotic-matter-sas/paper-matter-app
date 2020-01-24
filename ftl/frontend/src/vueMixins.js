/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

// Usage of global mixin https://vuejs.org/v2/guide/mixins.html#Global-Mixin
// Each method should be prefixed with mixin to warn the developer that this method is coming from a mixin
const mixinAlert = function (message, error = false, error_details = null, title = "Notification") {
  if (error_details != null) {
    message += ` (${error_details})`;
  }

  this.$root.$bvToast.toast(message, {
    title: title,
    variant: error ? 'danger' : 'success',
    solid: true,
    toaster: 'b-toaster-bottom-right'
  });
};

const mixinAlertWarning = function (message, error_details = null, title = "Notification") {
  if (error_details != null) {
    message += ` (${error_details})`;
  }

  this.$root.$bvToast.toast(message, {
    title: title,
    variant: 'warning',
    solid: true,
    toaster: 'b-toaster-bottom-right'
  });
};

export {mixinAlert, mixinAlertWarning};
