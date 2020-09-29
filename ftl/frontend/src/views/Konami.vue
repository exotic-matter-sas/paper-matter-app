<!--
  - Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
  - Licensed under the BSL License. See LICENSE in the project root for license information.
  -->

<template>
  <main class="flex-grow">
    <b-container>
      <b-row align-h="center" class="m-2 text-center">
        <b-col>
          <b-button
            id="generate-missing-thumbnails"
            variant="primary"
            @click="generateMissingThumbnail"
            v-if="thumbnailProgress === 0"
          >
            {{ $t("Generate missing thumbnail") }}
          </b-button>
          <div v-if="thumbnailProgress > 0">
            <h5 class="mt-3">
              {{ $t("Thumbnail generation in progress...") }}
            </h5>
            <b-progress :max="max" show-progressanimated>
              <b-progress-bar :value="thumbnailProgress">
                <strong>{{ thumbnailProgress }} / {{ max }}</strong>
              </b-progress-bar>
            </b-progress>
          </div>
        </b-col>
      </b-row>
    </b-container>
  </main>
</template>

<i18n>
  fr:
    Generate missing thumbnail: Générer les miniatures manquantes
    Thumbnail generation in progress...: Génération des miniatures en cours...
    Unable to load more document: Erreur lors du chargement de la suite des documents
    Unable to refresh documents list: Erreur lors du chargement de la liste des documents
    Thumbnail created: Miniature générée
    Unable to create thumbnail: Erreur lors de la génération de la miniature
    An unknown error occurred while creating missing thumbnails: Une erreur inconnue est survenue duramt la génération des miniatures manquantes
    Finished processing missing thumbnails: Génération des miniatures manquantes terminée
</i18n>

<script>
import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
import axios from "axios";

export default {
  name: "Konami",
  mixins: [FTLThumbnailGenMixin],

  data() {
    return {
      thumbnailProgress: 0,
      max: 100,
    };
  },

  methods: {
    generateMissingThumbnail: function () {
      const vi = this;

      axios
        .get("/app/api/v1/documents?flat=true")
        .then(async (response) => {
          let documents = response.data;
          vi.max = response.data.count;

          while (documents !== null && documents.results.length > 0) {
            for (const doc of documents.results) {
              vi.thumbnailProgress += 1;
              if (doc["thumbnail_available"] === false) {
                await vi
                  .createThumbnailForDocument(doc)
                  .then((response) => {
                    vi.mixinAlert(this.$t("Thumbnail created"));
                  })
                  .catch((error) =>
                    vi.mixinAlert(this.$t("Unable to create thumbnail"), true)
                  );
              }
            }

            if (documents.next == null) {
              documents = null;
            } else {
              let resp = await axios.get(documents.next);
              documents = await resp.data;
            }
          }
        })
        .catch((error) => {
          vi.mixinAlert(
            this.$t(
              "An unknown error occurred while creating missing thumbnails"
            ),
            true
          );
        })
        .then(() => {
          vi.mixinAlert(this.$t("Finished processing missing thumbnails"));
          vi.thumbnailProgress = 0;
          vi.max = 100;
        });
    },
  },
};
</script>
