/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

(function () {
  'use strict';
  fetch('/accounts/2fa/fido2/api/login_begin', {method: 'POST',})
    .then(function (response) {
      if (response.ok) return response.arrayBuffer();
      throw new Error('No credential available to authenticate!');
    })
    .then(CBOR.decode)
    .then(function (options) {
      return navigator.credentials.get(options);
    })
    .then(function (assertion) {
      const response = CBOR.encode({
        "credentialId": new Uint8Array(assertion.rawId),
        "authenticatorData": new Uint8Array(assertion.response.authenticatorData),
        "clientDataJSON": new Uint8Array(assertion.response.clientDataJSON),
        "signature": new Uint8Array(assertion.response.signature)
      });
      let otp_token = document.getElementById("id_otp_token");
      otp_token.value = btoa(String.fromCharCode.apply(null, new Uint8Array(response)));
      let form = document.getElementById("user-form");
      form.submit();
    });
})();
