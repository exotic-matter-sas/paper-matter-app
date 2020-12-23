<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE in the project root for license information.
  -->

<template>
  <b-modal
    :id="modalId"
    ok-variant="primary"
    size="lg"
    :title="$t('Set a reminder for the document')"
    @show="getAlerts"
  >
    <div class="d-flex flex-column flex-sm-row justify-content-center">
      <div class="align-self-center">
        <b-calendar
          class="mx-2 my-2"
          v-model="value"
          :locale="$i18n.locale"
          :min="new Date()"
          start-weekday="1"
          value-as-date
        >
          <div class="d-flex" dir="ltr">
            <b-button
              size="sm"
              variant="outline-primary"
              class="ml-auto"
              @click="setTomorrow"
            >
              Tomorrow
            </b-button>
            <b-button
              size="sm"
              variant="outline-primary"
              class="ml-auto"
              @click="setNextWeek"
            >
              Next Week
            </b-button>
            <b-button
              size="sm"
              variant="outline-primary"
              class="ml-auto"
              @click="setNextMonth"
            >
              Next Month
            </b-button>
          </div>
        </b-calendar>
        <b-form-input
          v-model="note"
          :placeholder="$t('Note for reminder')"
        ></b-form-input>
      </div>

      <div class="mx-2 my-2 flex-grow-1">
        <b-list-group v-if="alerts.length > 0">
          <b-list-group-item
            v-for="alert in alerts"
            :key="alert.id"
            class="flex-column align-items-start"
          >
            <div class="d-flex w-100 justify-content-between">
              <h5 class="mb-1">
                {{ $moment.parseZone(alert.alert_on).format("LL") }}
              </h5>
              <b-button
                size="sm"
                variant="danger"
                @click="deleteAlert(alert.id)"
                >Delete</b-button
              >
            </div>

            <div class="mb-1">
              {{ alert.note }}
            </div>
          </b-list-group-item>
        </b-list-group>
        <span v-else>
          {{ $t("No alert has been set") }}
        </span>
      </div>
    </div>

    <template slot="modal-footer">
      <div class="flex-grow-1 text-muted text-left font-italic">
        <small class="text-muted ml-auto">{{
          $t(
            "We will send you an email at the chosen day. There is a limit of 5 alerts per documents."
          )
        }}</small>
      </div>
      <b-button variant="secondary" @click.prevent="$bvModal.hide(modalId)">
        {{ $t("Close") }}
      </b-button>
      <b-button
        variant="primary"
        @click.prevent="setAlert"
        :disabled="!value || alerts.length >= 5"
      >
        {{ $t("Add reminder") }}
      </b-button>
    </template>
  </b-modal>
</template>

<i18n>
fr:
  dd:dd

</i18n>

<script>
import axios from "axios";
import { axiosConfig } from "@/constants";

export default {
  name: "FTLAlertDocument",

  props: {
    // customize the id to allow multiple usage of this component at the same time
    modalId: {
      type: String,
      default: "modal-rename-document",
    },
    doc: {
      Object,
      required: true,
    },
  },

  data() {
    return {
      value: null,
      note: "",
      alerts: [],
    };
  },

  methods: {
    setTomorrow: function () {
      this.value = this.$moment().add(1, "days").startOf("day").toDate();
    },
    setNextWeek: function () {
      this.value = this.$moment().add(14, "days").startOf("day").toDate();
    },
    setNextMonth: function () {
      this.value = this.$moment().add(1, "months").startOf("day").toDate();
    },

    getAlerts: function () {
      axios
        .get("/app/api/v1/documents/" + this.doc.pid + "/alerts")
        .then((response) => {
          this.alerts = response.data["results"];
        })
        .catch((error) => {
          this.mixinAlert(
            this.$t("Could not retrieve the list of alerts"),
            true
          );
        });
    },

    setAlert: function (bvModalEvt) {
      bvModalEvt.preventDefault();

      const alert_on = this.$moment(this.value).startOf("day").toDate();
      let body = { alert_on: alert_on, note: this.note };

      axios
        .post(
          "/app/api/v1/documents/" + this.doc.pid + "/alerts",
          body,
          axiosConfig
        )
        .then((response) => {
          this.alerts.push(response.data);

          this.$emit("event-document-alert", {
            alert: response.data,
          });

          this.value = null;
          this.note = "";
          this.mixinAlert(this.$t("Document alert set"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not set alert for document"), true);
        });
    },

    deleteAlert: function (alert_id) {
      axios
        .delete(
          "/app/api/v1/documents/" + this.doc.pid + "/alerts/" + alert_id,
          axiosConfig
        )
        .then((response) => {
          this.alerts = this.alerts.filter((item) => item.id !== alert_id);
          this.mixinAlert(this.$t("Document alert deleted"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not delete alert for document"), true);
        });
    },
  },
};
</script>

<style scoped></style>
