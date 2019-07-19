<template>
  <b-container>
    <b-row class="m-2">
      <b-col>
        <b-button id="generate-missing-thumbnails" variant="primary" @click="generateMissingThumbnail" v-if="thumbnailProgress === 0">Generate missing
          thumbnail
        </b-button>
        <div v-if="thumbnailProgress > 0">
          <h5 class="mt-3">Thumbnail generation in progress...</h5>
          <b-progress :max="max" show-progressanimated>
            <b-progress-bar :value="thumbnailProgress">
              <strong>{{ thumbnailProgress }} / {{ max }}</strong>
            </b-progress-bar>
          </b-progress>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
  import FTLThumbnailGenMixin from "@/components/FTLThumbnailGenMixin";
  import axios from 'axios';

  export default {
    name: 'Konami',
    mixins: [FTLThumbnailGenMixin],

    data() {
      return {
        thumbnailProgress: 0,
        max: 100
      }
    },

    methods: {
      generateMissingThumbnail: function () {
        const vi = this;

        axios
          .get("/app/api/v1/documents?flat=true")
          .then(async response => {
            let documents = response.data;
            vi.max = response.data.count;

            while (documents !== null && documents.results.length > 0) {
              for (const doc of documents.results) {
                vi.thumbnailProgress += 1;
                if (doc['thumbnail_available'] === false) {
                  await vi.createThumbnailForDocument(doc)
                    .then(response => {
                      vi.mixinAlert("Thumbnail updated!");
                    })
                    .catch(error => vi.mixinAlert("Unable to update thumbnail", true));
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
          .catch(error => {
            vi.mixinAlert("An error occurred while updating thumbnail", true)
          })
          .then(() => {
            vi.mixinAlert("Finished updating thumbnail");
            vi.thumbnailProgress = 0;
            vi.max = 100;
          });
      }
    }
  }
</script>

<style scoped>
</style>
