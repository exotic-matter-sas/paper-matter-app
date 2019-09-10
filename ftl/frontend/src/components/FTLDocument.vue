<template>
  <b-col cols="12" mb="4" sm="6" md="4" lg="3" xl="2" class="mb-3 document-thumbnail" :id="doc.pid"
         @click.ctrl="clickDoc">
    <div class="card" :class="{'selected': storeSelected}">
      <div class="card-img-top" slot="aside"
           :style="{'background-image': 'url(' + doc.thumbnail_url + ')'}"
           @click.exact="$emit('event-open-doc', doc.pid)"></div>
      <b-card-body>
        <b-card-title class="text-truncate document-title">{{ doc.title }}</b-card-title>
        <b-button class="m-1" variant="secondary" size="sm" :href="'uploads/' + doc.pid">
          <font-awesome-icon icon="file-download" :alt="this.$_('Download')"/>
        </b-button>
      </b-card-body>
      <b-card-footer :title="$moment(doc.created).format('LLLL')">
        <b-row align-h="between" align-v="center">
          <b-col class="p-1">
            <b-form-checkbox v-model="storeSelected" :title="$_('Use CTRL + left click for quick selection')"/>
          </b-col>
          <b-col cols="10" class="p-1"><small class="text-muted">{{ $moment(doc.created).fromNow() }}</small></b-col>
        </b-row>
      </b-card-footer>
    </div>
  </b-col>
</template>

<script>
  export default {
    props: {
      doc: {
        type: Object,
        required: true
      }
    },

    data() {
      return {}
    },

    computed: {
      storeSelected: {
        get: function () {
          // tick the checkbox if we found the document in the selected document list in vuex store
          return this.$store.state.selectedDocumentsHome.findIndex(x => x.pid === this.doc.pid) > -1;
        },

        set: function (value) {
          // update the store
          if (value === true) {
            this.$store.commit("selectDocument", this.doc)
          } else {
            this.$store.commit("unselectDocument", this.doc)
          }
        }
      }
    },

    methods: {
      openDoc: function () {
        this.$emit('event-open-doc', this.doc.pid);
      },

      clickDoc: function () {
        this.storeSelected = this.storeSelected !== true;
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../styles/customBootstrap.scss';

  .document-title {
    color: map_get($theme-colors, 'primary');
  }

  .card {
    border-color: rgba(0, 0, 0, 0.250);
    border-radius: calc(0.25rem - 1px);

    &:hover {
      border-color: map_get($theme-colors, 'primary');
    }
  }

  .selected {
    border-color: transparent;
    box-shadow: 0 0 0 2px  map_get($theme-colors, 'active');

    &:hover {
      border-color: transparent;
      box-shadow: 0 0 0 2px map_get($theme-colors, 'primary');
    }
  }

  .card-img-top {
    height: 200px;
    box-shadow: inset 0 -10px 30px -30px #0A0A0A;
    background-repeat: no-repeat;
    background-size: cover;
    transition: background-position 1.2s cubic-bezier(.68, -0.55, .27, 1.55) 1s,
    box-shadow 1.2s ease-in-out 1s;
    cursor: pointer;
    border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  }

  .card-title {
    cursor: pointer;
    font-size: 1.1rem;
  }

  .card-img-top:hover {
    background-position: bottom;
    box-shadow: inset 0 10px 30px -30px #0A0A0A;
  }

  .card-footer {
    &:first-letter {
      text-transform: capitalize;
    }

    text-align: center;
    font-size: 0.9em;
    padding: 0.25rem 1.25rem;
    font-style: italic;
  }
</style>
