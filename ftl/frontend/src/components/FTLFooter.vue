<!--
  - Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
  - Licensed under the Business Source License. See LICENSE at project root for more information.
  -->

<template>
  <footer class="footer mt-auto py-3 text-muted text-center">
    <i18n path="label" tag="p">
      <template v-slot:pm>
        <a id="pm-link" target="_blank" href="https://welcome.papermatter.app"
          >Paper Matter</a
        >
      </template>
      <template v-slot:em>
        <a id="em-link" target="_blank" href="https://www.exotic-matter.fr">
          Exotic <span class="highlight">Matter</span>
        </a>
      </template>
    </i18n>
  </footer>
</template>

<i18n>
  en:
    label: "{pm}, carefully crafted by {em} in France."
  fr:
    label: "{pm}, soigneusement conçu par {em} en France."
</i18n>

<style scoped>
#em-link {
  font-weight: bold;
}
</style>
