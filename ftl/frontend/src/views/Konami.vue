<template>
  <b-container>
    <b-row class="m-2">
      <b-col>
        <b-button variant="primary" @click="generateMissingThumbnail" v-if="thumbnailProgress === 0">Generate missing
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
  import axios from 'axios';
  import {createThumbFromUrl} from "@/thumbnailGenerator";
  import {axiosConfig} from "@/constants";

  export default {
    name: 'Konami',

    data() {
      return {
        thumbnailProgress: 0,
        max: 100
      }
    },

    methods: {
      createThumbnailForDocument: async function (doc, updateDocuments = true) {
        const vi = this;
        let thumb64;

        try {
          thumb64 = await createThumbFromUrl('/app/uploads/' + doc.pid);
        } catch (e) {
          vi.mixinAlert("Unable to update thumbnail", true);
          return;
        }

        let jsonData = {'thumbnail_binary': thumb64};

        axios
          .patch('/app/api/v1/documents/' + doc.pid, jsonData, axiosConfig)
          .then(response => {
          })
          .catch(error => vi.mixinAlert("Unable to update thumbnail", true));
      },

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
                  await vi.createThumbnailForDocument(doc, false);
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
