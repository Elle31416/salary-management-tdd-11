import axios from 'axios'

// In production (Vercel) VITE_API_URL = https://salary-management-tdd.onrender.com
// In development the Vite proxy rewrites /api → localhost:8000
const BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({ baseURL: BASE })

// Employees
export const fetchEmployees = (params) =>
  api.get('/employees', { params }).then(r => r.data)

export const fetchEmployee = (id) =>
  api.get(`/employees/${id}`).then(r => r.data)

export const createEmployee = (data) =>
  api.post('/employees', data).then(r => r.data)

export const updateEmployee = (id, data) =>
  api.put(`/employees/${id}`, data).then(r => r.data)

export const deleteEmployee = (id) =>
  api.delete(`/employees/${id}`)

// Insights
export const fetchSummary = () =>
  api.get('/insights/summary').then(r => r.data)

export const fetchSalaryByCountry = () =>
  api.get('/insights/salary-by-country').then(r => r.data)

export const fetchSalaryByTitle = () =>
  api.get('/insights/salary-by-title').then(r => r.data)

export const fetchDistribution = () =>
  api.get('/insights/salary-distribution').then(r => r.data)

export const fetchHeadcountByDept = () =>
  api.get('/insights/headcount-by-department').then(r => r.data)

export const fetchTopPaidTitles = () =>
  api.get('/insights/top-paid-titles').then(r => r.data)
