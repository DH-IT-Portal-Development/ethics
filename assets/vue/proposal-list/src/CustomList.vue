<script setup>
import {DSCList} from "cdh-vue-lib/components";
import {useI18n} from "vue-i18n";

// Required stuff
const props = defineProps(['config']);

const {t} = useI18n()

function formatDate(date) {
  return new Date(date).toLocaleString("nl-NL")
}
</script>

<!-- Here you can define your translations. Please remember to use `t` in your template instead of `$t` -->
<i18n>
{
  "en": {
    "name": "Name",
    "refnum": "Reference Number",
    "status": "Status"
  },
  "nl": {
    "name": "Naam",
    "refnum": "Referentie Nummer",
    "status": "Status"
  }
}
</i18n>

<template>
  <!-- Required stuff -->
  <DSCList :config="config">
    <template #data="{data, isLoading}">
      <!-- Custom stuff -->
      <!-- Add your table here -->
      <div class="mb-4">
        <div v-if="isLoading">
          <!-- Show a 'loading' message if data is being loaded -->
          Loading...
        </div>
        <div v-else>
          <div class="proposal-header">
            <div class="title">{{ t('name') }}</div>
            <div class="status">{{ t('status') }}</div>
          </div>
          <div class="proposal" v-for="item in data" :key="item.id">
            <div class="title text-truncate" :title="item.title">{{ item.title }}</div>
            <div class="description text-muted">
              <div class="reference-number">
                {{ item.reference_number }}
              </div>

              <span v-if="item.type" class="type"> | {{item.type}}</span>

            </div>

              <div class="status align-middle">{{item.short_status}}</div>
<!--            <div class="align-middle">{{item.get_status_display}}</div>-->
<!--            <div class="align-middle">{{formatDate(item.date_modified)}}</div>-->

          </div>
        </div>
      </div>
      <!-- end custom stuff, begin required stuff -->
    </template>
  </DSCList>
</template>

<style lang="scss" scoped>
.proposal {
  display: grid;
  padding: 1rem .5rem;

  .title {
    font-weight: bolder;
    //font-size: 1.2rem;
  }

  .description {
    display: flex;

  }
}
.proposal, .proposal-header {
  display: grid;
  grid-template-columns: 1fr  0.5fr 0.5fr;
  gap: 3px 3px;

  border-bottom: 1px solid var(--bs-border-color);
}
.proposal-header {

  grid-template-rows: auto;
  grid-template-areas:
    "title status actions";
  font-weight: bolder;
  padding: 0 .5rem 0.2rem;
}
.proposal {
  grid-template-rows: auto 1fr;
  grid-template-areas:
    "title status actions"
    "description status actions"
}
.title { grid-area: title; }
.status { grid-area: status; }
.description { grid-area: description; }
.actions { grid-area: actions; }

.status, .actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>
