<script>
  import {createThumbFromUrl} from "@/thumbnailGenerator";
  import axios from 'axios';
  import {axiosConfig} from "@/constants";


  export default {
    name: 'FTLThumbnailGenMixin',

    methods: {
      createThumbnailForDocument: async function (doc) {
        const vi = this;
        let thumb64;

        try {
          thumb64 = await createThumbFromUrl('/app/uploads/' + doc.pid);
        } catch (e) {
          vi.mixinAlert("Unable to update thumbnail", true);
          return;
        }

        let jsonData = {'thumbnail_binary': thumb64};

        return axios.patch('/app/api/v1/documents/' + doc.pid, jsonData, axiosConfig)
      }
    }
  }
</script>
