<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-modal
    :id="modalId"
    :title="$t('Share document')"
    ok-variant="primary"
    cancel-variant="danger"
    :cancel-title="$t('Unshare')"
    :ok-disabled="sharing"
    :cancel-disabled="sharing || unsharing"
    @ok="copyClipboard"
    @cancel="cancelSharing"
    @show="doSharing"
  >
    <b-container>
      <b-form-group
        id="fieldset-document-sharing"
        :description="
          $t('Anyone with the link will be able to see your document.')
        "
        :label="$t('Link to share')"
        label-for="document-sharing-link"
        label-class="text-truncate"
      >
        <b-form-input
          id="document-sharing-link"
          @focus.native="$event.target.select()"
          readonly
          :value="sharingLink"
        ></b-form-input>
      </b-form-group>
    </b-container>

    <template slot="modal-ok">
      <b-spinner :class="{ 'd-none': !sharing }" small></b-spinner>
      <span :class="{ 'd-none': sharing }">{{ $t("Copy to clipboard") }}</span>
    </template>
  </b-modal>
</template>

<i18n>
  fr:
    Unshare: Annuler le partage
    Share document: Partage du document
    Link to share: Lien à partager
    Anyone with the link will be able to see your document.: Tout le monde pourra accéder à votre document.
    Copy to clipboard: Copier dans le presse-papier
    Could not share document: Le document n'a pu être partagé
    Could not get share link: Le lien de partage n'a pu être récupéré
    Could not unshare document: Le partage du document n'a pu être interrompu
    Link copied: Lien copié
</i18n>
<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLDocumentSharing",

  props: {
    // customize the id to allow multiple usage of this component at the same time
    modalId: {
      type: String,
      default: "modal-document-sharing",
    },
    doc: {
      Object,
      required: true,
    },
  },

  data() {
    return { shareData: {}, sharing: false, unsharing: false };
  },

  computed: {
    sharingLink: function () {
      if (this.shareData && "public_url" in this.shareData) {
        return this.shareData.public_url;
      } else {
        return "";
      }
    },
  },

  methods: {
    doSharing: function () {
      this.sharing = true;
      axios
        .get("/app/api/v1/documents/" + this.doc.pid + "/share", axiosConfig)
        .then((response) => {
          if (response.data.count > 0) {
            this.shareData = response.data.results[0];
          } else {
            axios
              .post(
                "/app/api/v1/documents/" + this.doc.pid + "/share",
                {},
                axiosConfig
              )
              .then((response) => {
                this.shareData = response.data;
                this.$emit("event-document-shared");
              })
              .catch((error) => {
                this.mixinAlert(this.$t("Could not share document"), true);
              })
              .finally(() => (this.sharing = false));
          }
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not get share link"), true);
        })
        .finally(() => (this.sharing = false));
    },
    cancelSharing: function () {
      this.unsharing = true;
      axios
        .delete(
          "/app/api/v1/documents/" +
            this.doc.pid +
            "/share/" +
            this.shareData.pid,
          axiosConfig
        )
        .then((response) => {
          this.$emit("event-document-unshared");
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not unshare document"), true);
        })
        .finally(() => (this.unsharing = false));
    },
    copyClipboard: function () {
      navigator.clipboard
        .writeText(this.sharingLink)
        .then(() => this.mixinAlert(this.$t("Link copied")))
        .finally(() => this.$bvModal.hide(this.modalId));
    },
  },
};
</script>
