/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import mutations from "@/store/mutations";
import getters from "@/store/getters";

const state = {
  selectedMoveTargetFolder: null,
  panelSelectedFolder: null,
  selectedDocumentsHome: [],
  sortHome: 'recent',
  ftlAccount: {
    'name': '...',
    'isSuperUser': false,
    'otp_warning': false,
    'supported_exts': [],
  }
};

export default {
  state,
  getters,
  mutations
}
