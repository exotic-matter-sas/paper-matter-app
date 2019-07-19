// Usage of global mixin https://vuejs.org/v2/guide/mixins.html#Global-Mixin
// Each method should be prefixed with mixin to warn the developer that this method is coming from a mixin
const mixinAlert = function (message, error = false, error_details = null, title = "Notification") {
  if (error_details != null) {
    message += ` (${error_details})`;
  }
  this.$bvToast.toast(message, {
    title: title,
    variant: error ? 'danger' : 'success',
    solid: true,
    toaster: 'b-toaster-bottom-right'
  });
};

export {mixinAlert};
