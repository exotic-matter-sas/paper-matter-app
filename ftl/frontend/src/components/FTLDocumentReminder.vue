<!--
  - Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <b-modal
    :id="modalId"
    ok-variant="primary"
    size="lg"
    :title="$t('Set document reminders')"
    @show="init"
  >
    <b-row>
      <b-col
        v-if="showAddPanel"
        class="border-right border-lg-secondary"
        :title="
          reminders.length >= 5
            ? $t('You cannot add more than 5 reminders to a document')
            : ''
        "
      >
        <b-calendar
          v-model="value"
          :locale="$i18n.locale"
          :min="
            this.$moment
              .utc()
              .utcOffset(this.ftlAccount['tz_offset'])
              .add(1, 'days')
              .startOf('day')
              .format('YYYY-MM-DD')
          "
          :initial-date="
            this.$moment
              .utc()
              .utcOffset(this.ftlAccount['tz_offset'])
              .startOf('day')
              .format('YYYY-MM-DD')
          "
          start-weekday="1"
          :disabled="reminders.length >= 5"
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
          hide-header
          block
        >
          <div class="d-flex justify-content-center">
            <b-button-group size="sm" class="w-100">
              <b-button
                variant="outline-primary"
                class="text-truncate"
                @click="setTomorrow"
                :disabled="reminders.length >= 5"
              >
                {{ $t("Tomorrow") }}
              </b-button>
              <b-button
                variant="outline-primary"
                class="text-truncate"
                @click="setNextWeek"
                :disabled="reminders.length >= 5"
              >
                {{ $t("Next week") }}
              </b-button>
              <b-button
                variant="outline-primary"
                class="text-truncate"
                @click="setNextMonth"
                :disabled="reminders.length >= 5"
              >
                {{ $t("Next month") }}
              </b-button>
            </b-button-group>
          </div>
        </b-calendar>
        <b-form-input
          id="reminder-note"
          class="mt-2"
          v-model="note"
          :placeholder="$t('Reminder note (optional)')"
          :disabled="reminders.length >= 5"
        ></b-form-input>
      </b-col>
      <b-col v-if="showListPanel">
        <b-list-group v-if="reminders.length > 0">
          <b-list-group-item v-for="reminder in reminders" :key="reminder.id">
            <div
              class="d-flex w-100 align-items-center justify-content-between"
            >
              <h5 class="mb-0">
                <font-awesome-icon
                  :icon="['far', 'calendar-alt']"
                  class="mr-2"
                />
                <span :title="reminder.alert_on">{{
                  $moment.parseZone(reminder.alert_on).format("LL")
                }}</span>
              </h5>
              <b-button
                size="sm"
                variant="danger"
                @click="deleteReminder(reminder.id)"
                >{{ $t("Delete") }}</b-button
              >
            </div>

            <div
              v-if="reminder.note !== ''"
              class="text-muted text-wrap text-break"
            >
              {{ reminder.note }}
            </div>
          </b-list-group-item>
        </b-list-group>
        <div
          v-else
          class="d-flex align-items-center justify-content-center h-100"
        >
          <span class="text-muted">
            {{ $t("No reminder has been set") }}
          </span>
        </div>
      </b-col>
    </b-row>

    <template slot="modal-footer">
      <b-row no-gutters class="w-100">
        <b-col
          class="d-flex justify-content-start align-items-center flex-grow-1"
        >
          <small class="text-muted">{{
            $t(
              "We will send you an email at the chosen days. There is a limit of 5 reminders per document."
            )
          }}</small>
        </b-col>
        <b-col
          v-if="showAddPanel"
          class="d-flex justify-content-end align-items-start flex-grow-0"
        >
          <b-button
            v-if="!showListPanel"
            class="mr-1"
            variant="secondary"
            @click.prevent="showPanels({ listPanel: true, addPanel: false })"
          >
            {{ $t("Cancel") }}
          </b-button>
          <b-button
            class="text-nowrap"
            variant="primary"
            @click.prevent="setReminder"
            :disabled="!value || reminders.length >= 5"
            :title="
              reminders.length >= 5
                ? $t('You cannot add more than 5 reminders to a document')
                : ''
            "
          >
            {{
              showListPanel === false ? $t("Save reminder") : $t("Add reminder")
            }}
          </b-button>
        </b-col>
        <b-col
          v-else
          class="d-flex justify-content-end align-items-start flex-grow-0"
        >
          <b-button
            class="text-nowrap"
            variant="primary"
            @click.prevent="showPanels({ listPanel: false, addPanel: true })"
            :disabled="reminders.length >= 5"
            :title="
              reminders.length >= 5
                ? $t('You cannot add more than 5 reminders to a document')
                : ''
            "
          >
            {{ $t("Add reminder") }}
          </b-button>
        </b-col>
      </b-row>
    </template>
  </b-modal>
</template>

<i18n>
fr:
  Set document reminders: Fixer des rappels pour le document
  We will send you an email at the chosen days. There is a limit of 5 reminders per document.: Nous vous enverrons un email les jours choisis. Il y a une limite de 5 rappels par document.
  Close: Fermer
  No reminder has been set: Aucun rappel défini
  Add reminder: Ajouter un rappel
  Tomorrow: Demain
  Next week: Semaine prochaine
  Next month: Mois prochain
  Reminder note (optional): Note pour le rappel (optionnel)
  Delete: Supprimer
  Could not retrieve the list of reminders: Impossible de récupérer la liste des rappels
  Reminder was added: Un rappel a été ajouté
  Could not add reminder: Impossible d'ajouter le rappel
  Reminder deleted: Le rappel a été supprimé
  Could not delete reminder: Impossible de supprimer le rappel
  Current month: Mois courant
  Use cursor keys to navigate calendar dates: Utilisez les touches fléchées du clavier pour naviguer dans le calendrier
  Calendar navigation: Navigation dans le calendrier
  Next year: Année suivante
  No date selected: Aucune date sélectionnée
  Previous month: Mois précédent
  Previous year: Année précédente
  Selected date: Date sélectionnée
  Today: Aujourd'hui
  You cannot add more than 5 reminders to a document: Vous ne pouvez ajouter plus de 5 rappels par document
</i18n>

<script>
import axios from "axios";
import { axiosConfig } from "@/constants";
import { mapState } from "vuex";

export default {
  name: "FTLDocumentReminder",

  props: {
    // customize the id to allow multiple usage of this component at the same time
    modalId: {
      type: String,
      default: "modal-document-reminder",
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
      reminders: [],
      showListPanel: false,
      showAddPanel: false,
    };
  },

  computed: {
    mobileMode: function () {
      return window.matchMedia("(max-width: 992px)").matches;
    },
    ...mapState(["ftlAccount"]), // generate vuex computed getter
  },

  methods: {
    init: function () {
      // In mobile mode only show 1 of the 2 panels
      if (this.mobileMode) {
        if (this.doc.reminders_count > 0) {
          this.showPanels({ listPanel: true, addPanel: false });
        } else {
          this.showPanels({ listPanel: false, addPanel: true });
        }
      }
      // In desktop mode show the 2 panels
      else {
        this.showPanels({ listPanel: true, addPanel: true });
      }

      // Get reminders list if needed
      if (this.doc.reminders_count > 0) {
        this.getReminders();
      }
    },

    setTomorrow: function () {
      // Convert the local time to the account timezone to deal with users choosing explicitly
      // a different timezone than the one on their computer
      this.value = this.$moment
        .utc()
        .utcOffset(this.ftlAccount["tz_offset"])
        .add(1, "days")
        .startOf("day")
        .format("YYYY-MM-DD");
    },
    setNextWeek: function () {
      this.value = this.$moment
        .utc()
        .utcOffset(this.ftlAccount["tz_offset"])
        .add(7, "days")
        .startOf("day")
        .format("YYYY-MM-DD");
    },
    setNextMonth: function () {
      this.value = this.$moment
        .utc()
        .utcOffset(this.ftlAccount["tz_offset"])
        .add(1, "months")
        .startOf("day")
        .format("YYYY-MM-DD");
    },

    getReminders: function () {
      axios
        .get("/app/api/v1/documents/" + this.doc.pid + "/reminders")
        .then((response) => {
          this.reminders = response.data["results"];
        })
        .catch((error) => {
          this.mixinAlert(
            this.$t("Could not retrieve the list of reminders"),
            true
          );
        });
    },

    setReminder: function (bvModalEvt) {
      bvModalEvt.preventDefault();

      // Convert the local time to the account timezone to deal with users choosing explicitly
      // a different timezone than the one on their computer
      const alert_on = this.$moment
        .utc(this.value)
        .utcOffset(this.ftlAccount["tz_offset"], true)
        .startOf("day");
      let body = { alert_on: alert_on, note: this.note };

      axios
        .post(
          "/app/api/v1/documents/" + this.doc.pid + "/reminders",
          body,
          axiosConfig
        )
        .then((response) => {
          this.reminders.push(response.data);
          this.reminders = this.reminders.sort((a, b) =>
            a.alert_on.localeCompare(b.alert_on)
          );

          this.$emit("event-document-reminders-updated", {
            alert: response.data,
            reminders_count: this.reminders.length,
          });

          this.value = null;
          this.note = "";
          this.mixinAlert(this.$t("Reminder was added"));

          // if mobile mode switch to list panel
          if (this.mobileMode) {
            this.showListPanel = true;
            this.showAddPanel = false;
          }
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not add reminder"), true);
        });
    },

    deleteReminder: function (alert_id) {
      axios
        .delete(
          "/app/api/v1/documents/" + this.doc.pid + "/reminders/" + alert_id,
          axiosConfig
        )
        .then((response) => {
          this.reminders = this.reminders.filter(
            (item) => item.id !== alert_id
          );

          this.$emit("event-document-reminders-updated", {
            reminders_count: this.reminders.length,
          });

          this.mixinAlert(this.$t("Reminder deleted"));
        })
        .catch((error) => {
          this.mixinAlert(this.$t("Could not delete reminder"), true);
        });
    },

    dateDisabled: function (ymd, theDate) {
      const currentDate = this.$moment
        .utc(ymd)
        .utcOffset(this.ftlAccount["tz_offset"], true);
      for (const reminder of this.reminders) {
        // Only compare up to the day (don't compare time)
        if (currentDate.isSame(reminder.alert_on, "day")) {
          return true;
        }
      }

      return false;
    },

    showPanels: function ({ listPanel, addPanel }) {
      this.showListPanel = listPanel;
      this.showAddPanel = addPanel;
    },
  },
};
</script>

<style scoped></style>
