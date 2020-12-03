/*
 * Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
 * Licensed under the Business Source License. See LICENSE at project root for more information.
 */

import mutations from "@/store/mutations";
import getters from "@/store/getters";

const state = {
  previousLevels: [], // breadcrumb
  selectedMoveTargetFolder: null,
  panelSelectedFolder: null,
  selectedDocumentsHome: [],
  sortHome: "recent",
  lastOpenedDocument: null,
  ftlAccount: {
    name: "...",
    isSuperUser: false,
    otp_warning: false,
    supported_exts: [],
  },
};

export default {
  state,
  getters,
  mutations,
};
