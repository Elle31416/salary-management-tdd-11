import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { createEmployee, updateEmployee } from '../lib/api'

const COUNTRIES = ['USA', 'UK', 'Germany', 'Canada', 'Australia', 'India', 'France', 'Brazil', 'Japan', 'Netherlands']
const DEPARTMENTS = ['Engineering', 'Sales', 'Marketing', 'Finance', 'HR', 'Operations', 'Legal', 'Product', 'Design', 'Support']
const CURRENCIES = { USA: 'USD', UK: 'GBP', Germany: 'EUR', Canada: 'CAD', Australia: 'AUD', India: 'INR', France: 'EUR', Brazil: 'BRL', Japan: 'JPY', Netherlands: 'EUR' }

const EMPTY = {
  name: '', email: '', job_title: '', department: DEPARTMENTS[0],
  country: COUNTRIES[0], salary: '', currency: 'USD',
  employment_status: 'active', hire_date: ''
}

export default function EmployeeModal({ mode, employee, onClose }) {
  const qc = useQueryClient()
  const [form, setForm] = useState(mode === 'edit' ? { ...employee } : EMPTY)
  const [errors, setErrors] = useState({})

  const mut = useMutation({
    mutationFn: mode === 'edit'
      ? (data) => updateEmployee(employee.id, data)
      : createEmployee,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['employees'] })
      qc.invalidateQueries({ queryKey: ['summary'] })
      onClose()
    },
    onError: (err) => {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') setErrors({ _: detail })
    },
  })

  const set = (k, v) => {
    setForm(f => {
      const next = { ...f, [k]: v }
      if (k === 'country') next.currency = CURRENCIES[v] || 'USD'
      return next
    })
    setErrors(e => ({ ...e, [k]: '' }))
  }

  const validate = () => {
    const e = {}
    if (!form.name.trim()) e.name = 'Required'
    if (!form.email.trim()) e.email = 'Required'
    if (!form.job_title.trim()) e.job_title = 'Required'
    if (!form.salary || Number(form.salary) <= 0) e.salary = 'Must be > 0'
    if (!form.hire_date) e.hire_date = 'Required'
    return e
  }

  const submit = (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    mut.mutate({ ...form, salary: Number(form.salary) })
  }

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-[--surface] border border-[--border] rounded-xl w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[--border]">
          <h2 className="font-display text-lg text-[--text]">
            {mode === 'edit' ? 'Edit Employee' : 'Add Employee'}
          </h2>
          <button onClick={onClose} className="p-1.5 rounded hover:bg-[--surface2] text-[--muted] hover:text-[--text] transition-colors">
            <X size={16} />
          </button>
        </div>

        <form onSubmit={submit} className="p-6 space-y-4">
          {errors._ && (
            <div className="text-sm text-red-400 bg-red-400/10 rounded-lg px-3 py-2">{errors._}</div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <Field label="Full Name" error={errors.name}>
              <input {...inp} value={form.name} onChange={e => set('name', e.target.value)} placeholder="Jane Smith" />
            </Field>
            <Field label="Email" error={errors.email}>
              <input {...inp} type="email" value={form.email} onChange={e => set('email', e.target.value)} placeholder="jane@company.com" />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Job Title" error={errors.job_title}>
              <input {...inp} value={form.job_title} onChange={e => set('job_title', e.target.value)} placeholder="Software Engineer" />
            </Field>
            <Field label="Department">
              <select {...sel} value={form.department} onChange={e => set('department', e.target.value)}>
                {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
              </select>
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Country">
              <select {...sel} value={form.country} onChange={e => set('country', e.target.value)}>
                {COUNTRIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </Field>
            <Field label="Status">
              <select {...sel} value={form.employment_status} onChange={e => set('employment_status', e.target.value)}>
                <option value="active">Active</option>
                <option value="on_leave">On Leave</option>
                <option value="terminated">Terminated</option>
              </select>
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Salary" error={errors.salary}>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[--muted] text-sm">{form.currency}</span>
                <input {...inp} type="number" value={form.salary} onChange={e => set('salary', e.target.value)}
                  placeholder="120000" className={`${inp.className} pl-12`} />
              </div>
            </Field>
            <Field label="Hire Date" error={errors.hire_date}>
              <input {...inp} type="date" value={form.hire_date} onChange={e => set('hire_date', e.target.value)} />
            </Field>
          </div>

          <div className="flex gap-3 pt-2 justify-end">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg border border-[--border] text-[--muted] hover:text-[--text] transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={mut.isPending}
              className="px-5 py-2 text-sm rounded-lg bg-[--gold] text-[--bg] font-medium hover:bg-yellow-300 transition-colors disabled:opacity-50">
              {mut.isPending ? 'Saving…' : mode === 'edit' ? 'Save Changes' : 'Add Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Field({ label, error, children }) {
  return (
    <div>
      <label className="block text-xs font-medium text-[--muted] mb-1.5 uppercase tracking-wider">{label}</label>
      {children}
      {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
    </div>
  )
}

const inp = {
  className: 'w-full px-3 py-2 text-sm bg-[--ink-900] bg-[color:var(--bg)] border border-[--border] rounded-lg text-[--text] placeholder:text-[--muted] focus:outline-none focus:border-[--teal] transition-colors',
}
const sel = {
  className: 'w-full px-3 py-2 text-sm bg-[color:var(--bg)] border border-[--border] rounded-lg text-[--text] focus:outline-none focus:border-[--teal] transition-colors cursor-pointer',
}
