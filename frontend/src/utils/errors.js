// Приводит ошибку DRF/Axios к одной читаемой строке.
export function extractError(error) {
  const data = error?.response?.data
  if (!data) return 'Не удалось выполнить запрос. Проверьте соединение.'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  // DRF обычно возвращает объект {поле: ["ошибка", ...]}.
  const first = Object.values(data)[0]
  if (Array.isArray(first) && first.length) return String(first[0])
  if (typeof first === 'string') return first
  return 'Не удалось выполнить запрос.'
}

// Для ответов с responseType: 'blob' тело ошибки нужно прочитать как текст.
export async function extractBlobError(error) {
  const data = error?.response?.data
  if (data instanceof Blob) {
    try {
      const parsed = JSON.parse(await data.text())
      if (parsed.detail) return parsed.detail
    } catch (e) {
      /* тело не JSON — игнорируем */
    }
  }
  return extractError(error)
}
