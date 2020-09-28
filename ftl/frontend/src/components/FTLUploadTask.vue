<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <b-col cols="12" mb="4" sm="6" md="4" lg="3" xl="2">
    <b-card no-body>
      <b-button
        class="interrupt-upload-task-button"
        :class="{ disabled: interrupted }"
        variant="link"
        @click="interrupt"
      >
        <font-awesome-icon
          icon="times-circle"
          :title="$t('Interrupt this upload')"
        />
      </b-button>
      <b-row
        class="align-items-center text-center py-3 text-secondary"
        no-gutters
      >
        <b-col cols="5">
          <font-awesome-icon icon="file" size="4x" />
          <br />
          <small class="text-primary font-weight-bold">
            {{ $tc("| 1 document | {n} documents", leftToUpload) }}
          </small>
        </b-col>
        <b-col cols="2">
          <font-awesome-icon icon="arrow-right" size="2x" />
        </b-col>
        <b-col cols="5">
          <font-awesome-icon icon="folder" size="4x" />
          <br />
          <small class="text-primary font-weight-bold">
            {{ folderName }}
          </small>
        </b-col>
      </b-row>
      <b-card-footer footer-tag="footer" footer-class="p-0 upload-tasks-loader">
        <b-progress
          v-show="currentUploadProgress === 0"
          value="100"
          max="100"
          class="upload-task-progress"
          animated
          variant="secondary"
        >
        </b-progress>
        <b-progress
          v-show="currentUploadProgress > 0"
          :value="currentUploadProgress"
          :max="totalUploadCount"
          class="upload-task-progress"
          animated
        >
        </b-progress>
      </b-card-footer>
    </b-card>
  </b-col>
</template>

<script>
export default {
  props: {
    folderName: {
      type: String,
      required: true,
    },
    leftToUpload: {
      type: Number,
      required: true,
    },
  },

  data() {
    return {
      interrupted: false,
      totalUploadCount: 0,
    };
  },

  mounted: function () {
    // At component creation, we store the number of documents to upload, to display progressbar
    this.totalUploadCount = this.leftToUpload;
  },

  watch: {
    leftToUpload: function (newVal, oldVal) {
      // if leftToUpload is increased after component creation, we need to update to totalUploadCount accordingly
      if (newVal > oldVal) {
        this.totalUploadCount += newVal - oldVal;
      }
    },
  },

  computed: {
    currentUploadProgress: function () {
      return this.totalUploadCount - this.leftToUpload;
    },
  },

  methods: {
    interrupt: function () {
      this.$emit("event-interrupt-task", this.$vnode.key);
      this.interrupted = true;
    },
  },
};
</script>

<style scoped lang="scss">
.interrupt-upload-task-button {
  font-size: 1.5em;
  padding: 0;
  border: 0;
  position: absolute;
  top: 0;
  right: 0;
  line-height: 1;
  margin-top: -0.5em;
  margin-right: -0.5em;
}

.upload-task-progress {
  border-radius: 0 0 calc(0.25rem - 1px) calc(0.25rem - 1px);
}
</style>
