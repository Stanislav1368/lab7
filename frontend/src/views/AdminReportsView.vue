<script setup>
import { onMounted, reactive, ref } from 'vue'

import api from '../api'
import { extractBlobError } from '../utils/errors'

const tables = ref([])
// selected[tableKey] = { enabled: boolean, fields: string[] }
const selected = reactive({})
const loading = ref(true)
const downloading = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    // Список доступных таблиц и полей формирует сервер (белый список).
    const { data } = await api.get('/reports/schema/')
    tables.value = data.tables
    data.tables.forEach((table) => {
      selected[table.key] = { enabled: false, fields: [] }
    })
  } catch (e) {
    error.value = 'Не удалось загрузить список таблиц. Проверьте права администратора.'
  } finally {
    loading.value = false
  }
})

function toggleTable(table) {
  const state = selected[table.key]
  state.enabled = !state.enabled
  // При включении таблицы по умолчанию выбираем все её поля.
  state.fields = state.enabled ? table.fields.map((field) => field.key) : []
}

function toggleField(table, field) {
  const state = selected[table.key]
  const index = state.fields.indexOf(field.key)
  if (index === -1) {
    state.fields.push(field.key)
  } else {
    state.fields.splice(index, 1)
  }
}

function buildPayload() {
  const payload = {}
  tables.value.forEach((table) => {
    const state = selected[table.key]
    if (state.enabled && state.fields.length) {
      payload[table.key] = [...state.fields]
    }
  })
  return payload
}

async function exportXlsx() {
  error.value = ''
  const payload = buildPayload()

  if (!Object.keys(payload).length) {
    error.value = 'Выберите хотя бы одну таблицу и хотя бы одно поле.'
    return
  }

  downloading.value = true
  try {
    const response = await api.post(
      '/reports/export/',
      { tables: payload },
      { responseType: 'blob' }
    )

    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `coffee_report_${new Date()
      .toISOString()
      .slice(0, 19)
      .replace(/[:T]/g, '-')}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = await extractBlobError(e)
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <section>
    <div class="page-head">
      <h1>Выгрузка отчётов в XLSX</h1>
      <span class="muted small">Доступно только администратору</span>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <p v-if="loading" class="muted">Загрузка списка таблиц…</p>

    <div v-else class="reports">
      <div v-for="table in tables" :key="table.key" class="card table-block">
        <h2>
          <label class="check-row">
            <input
              type="checkbox"
              :checked="selected[table.key].enabled"
              @change="toggleTable(table)"
            />
            {{ table.label }}
          </label>
        </h2>

        <div v-if="selected[table.key].enabled" class="field-grid">
          <label
            v-for="field in table.fields"
            :key="field.key"
            class="check-row"
          >
            <input
              type="checkbox"
              :checked="selected[table.key].fields.includes(field.key)"
              @change="toggleField(table, field)"
            />
            {{ field.label }}
          </label>
        </div>
      </div>

      <div class="report-actions">
        <button class="btn" type="button" :disabled="downloading" @click="exportXlsx">
          {{ downloading ? 'Формируем файл…' : 'Скачать XLSX' }}
        </button>
        <span class="muted small">
          Каждая выбранная таблица будет на отдельном листе.
        </span>
      </div>
    </div>
  </section>
</template>
