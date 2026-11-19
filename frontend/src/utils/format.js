// Форматирование цены в рублях: 790 -> "790,00 ₽".
export function formatPrice(value) {
  const number = Number(value || 0)
  return (
    number.toLocaleString('ru-RU', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }) + ' ₽'
  )
}

// Дата/время из ISO-строки в локальном формате.
export function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleString('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short'
  })
}
