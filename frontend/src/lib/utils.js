export const formatSalary = (val, currency = 'USD') =>
  new Intl.NumberFormat('en-US', {
    style: 'currency', currency, maximumFractionDigits: 0
  }).format(val)

export const formatNumber = (n) =>
  new Intl.NumberFormat('en-US').format(n)

export const STATUS_COLORS = {
  active: 'text-teal-400 bg-teal-400/10',
  on_leave: 'text-yellow-400 bg-yellow-400/10',
  terminated: 'text-red-400 bg-red-400/10',
}

export const STATUS_LABELS = {
  active: 'Active',
  on_leave: 'On Leave',
  terminated: 'Terminated',
}
