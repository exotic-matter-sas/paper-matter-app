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
          :date-disabled-fn="dateDisabled"
          :label-current-month="$t('Current month')"
          :label-help="$t('Use cursor keys to navigate calendar dates')"
          :label-nav="$t('Calendar navigation')"
          :label-next-month="$t('Next month')"
          :label-next-year="$t('Next year')"
          :label-no-date-selected="$t('No date selected')"
          :label-prev-month="$t('Previous month')"
          :label-prev-year="$t('Previous year')"
          :label-selected="$t('Selected date')"
          :label-today="$t('Today')"
        >
          <div class="d-flex flex-wrap justify-content-center">
            <b-button
              size="sm"
              variant="outline-primary"
              class="m-1 text-truncate"
              @click="setTomorrow"
            >
              {{ $t("For tomorrow") }}
            </b-button>
            <b-button
              size="sm"
              variant="outline-primary"
              class="m-1 text-truncate"
              @click="setNextWeek"
            >
              {{ $t("For next week") }}
            </b-button>
            <b-button
              size="sm"
              variant="outline-primary"
              class="m-1 text-truncate"
              @click="setNextMonth"
            >
              {{ $t("For next month") }}
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
                >{{ $t("Delete") }}</b-button
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
  Set a reminder for the document: Fixer un rappel pour le document
  We will send you an email at the chosen day. There is a limit of 5 alerts per documents.: Nous vous enverrons un email le jour choisi. Il y a une limite de 5 alertes par document.
  Close: Fermer
  Add reminder: Ajouter un rappel
  For tomorrow: Pour demain
  For next week: La semaine prochaine
  For next month: Le mois prochain
  Note for reminder: Note pour le rappel
  Delete: Supprimer
  Could not retrieve the list of reminders: Impossible de récupérer la liste des rappels
  Reminder was added: Un rappel a été ajouté
  Could not add reminder: Impossible d'ajouter le rappel
  Reminder deleted: Le rappel a été supprimé
  Could not delete reminder: Impossible de supprimer le rappel
  Current month: Mois courant
  Use cursor keys to navigate calendar dates: Utilisez les touches fléchées du clavier pour naviguer dans le calendrier
  Calendar navigation: Navigation dans le calendrier
  Next month: Mois suivant
  Next year: Année suivante
  No date selected: Aucune date sélectionnée
  Previous month: Mois précédent
  Previous year: Année précédente
  Selected date: Date sélectionnée
  Today: Aujourd'hui
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
            this.$t("Could not retrieve the list of reminders"),
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
          this.alerts = this.alerts.sort((a, b) =>
            a.alert_on.localeCompare(b.alert_on)
          );

          this.$emit("event-document-alert", {
            alert: response.data,
          });

          this.value = null;
          this.note = "";
          this.mixinAlert(this.$t("Reminder was added"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not add reminder"), true);
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
          this.mixinAlert(this.$t("Reminder deleted"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not delete reminder"), true);
        });
    },

    dateDisabled: function (ymd, theDate) {
      const currentDate = this.$moment(theDate);
      for (const alert of this.alerts) {
        if (currentDate.isSame(alert.alert_on)) {
          return true;
        }
      }

      return false;
    },
  },
};
</script>

<style scoped></style>
