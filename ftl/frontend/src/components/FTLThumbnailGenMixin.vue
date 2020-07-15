<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<script>
import { createThumbFromUrl } from "@/thumbnailGenerator";
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLThumbnailGenMixin",

  methods: {
    createThumbnailForDocument: async function (doc) {
      let thumb64;

      try {
        thumb64 = await createThumbFromUrl(doc.document_url);
      } catch (e) {
        return Promise.reject("Unable to create thumbnail");
      }

      let jsonData = { thumbnail_binary: thumb64 };

      return axios.patch(
        "/app/api/v1/documents/" + doc.pid,
        jsonData,
        axiosConfig
      );
    },
  },
};
</script>
