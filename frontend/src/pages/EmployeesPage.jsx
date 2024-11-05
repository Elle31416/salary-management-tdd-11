import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Plus, Pencil, Trash2, ChevronLeft, ChevronRight, X, Check, AlertCircle } from 'lucide-react'
import { fetchEmployees, deleteEmployee } from '../lib/api'
import { formatSalary, STATUS_COLORS, STATUS_LABELS } from '../lib/utils'
import EmployeeModal from '../components/EmployeeModal'

const COUNTRIES = ['USA', 'UK', 'Germany', 'Canada', 'Australia', 'India', 'France', 'Brazil', 'Japan', 'Netherlands']
const STATUSES = ['active', 'on_leave', 'terminated']

export default function EmployeesPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [country, setCountry] = useState('')
  const [status, setStatus] = useState('')
  const [modal, setModal] = useState(null) // null | { mode: 'create'|'edit', employee? }
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleteError, setDeleteError] = useState('')

  const params = { page, page_size: pageSize, ...(search && { search }), ...(country && { country }), ...(status && { status }) }

  const { data, isLoading } = useQuery({
    queryKey: ['employees', params],
    queryFn: () => fetchEmployees(params),
    keepPreviousData: true,
  })

  const deleteMut = useMutation({
    mutationFn: deleteEmployee,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['employees'] })
      setDeleteTarget(null)
    },
    onError: () => setDeleteError('Failed to delete. Try again.'),
  })

  const totalPages = data ? Math.ceil(data.total / pageSize) : 1

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl text-[--text]">Employees</h1>
          <p className="text-sm text-[--muted] mt-0.5">
            {data ? `${data.total.toLocaleString()} records` : 'Loading…'}
          </p>
        </div>
        <button onClick={() => setModal({ mode: 'create' })}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-[--gold] text-[--bg] hover:bg-yellow-300 transition-colors">
          <Plus size={14} />
          Add Employee
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5">
        <div className="relative flex-1 max-w-xs">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[--muted]" />
          <input
            className="w-full pl-9 pr-3 py-2 text-sm bg-[--surface] border border-[--border] rounded-lg text-[--text] placeholder:text-[--muted] focus:outline-none focus:border-[--teal] transition-colors"
            placeholder="Search name, email, title…"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
          />
        </div>
        <Select value={country} onChange={v => { setCountry(v); setPage(1) }} placeholder="All Countries">
          {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
        </Select>
        <Select value={status} onChange={v => { setStatus(v); setPage(1) }} placeholder="All Statuses">
          {STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </Select>
        {(search || country || status) && (
          <button onClick={() => { setSearch(''); setCountry(''); setStatus(''); setPage(1) }}
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-[--muted] hover:text-[--text] transition-colors">
            <X size={13} /> Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-[--border] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[--border]" style={{ background: 'var(--surface)' }}>
                {['Name', 'Job Title', 'Department', 'Country', 'Salary', 'Status', 'Hired', ''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-[--muted] uppercase tracking-wider whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i} className="border-b border-[--border]">
                    {Array.from({ length: 8 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 rounded bg-[--surface2] animate-pulse" style={{ width: `${60 + Math.random() * 40}%` }} />
                      </td>
                    ))}
                  </tr>
                ))
              ) : data?.items.map(emp => (
                <tr key={emp.id}
                  className="border-b border-[--border] hover:bg-[--surface] transition-colors group">
                  <td className="px-4 py-3">
                    <div className="font-medium text-[--text]">{emp.name}</div>
                    <div className="text-xs text-[--muted]">{emp.email}</div>
                  </td>
                  <td className="px-4 py-3 text-[--muted]">{emp.job_title}</td>
                  <td className="px-4 py-3 text-[--muted]">{emp.department}</td>
                  <td className="px-4 py-3 text-[--muted]">{emp.country}</td>
                  <td className="px-4 py-3 font-mono-code text-[--gold] font-medium">
                    {formatSalary(emp.salary, emp.currency)}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[emp.employment_status]}`}>
                      {STATUS_LABELS[emp.employment_status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[--muted] text-xs font-mono-code">{emp.hire_date}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => setModal({ mode: 'edit', employee: emp })}
                        className="p-1.5 rounded hover:bg-[--surface2] text-[--muted] hover:text-[--teal] transition-colors">
                        <Pencil size={13} />
                      </button>
                      <button onClick={() => { setDeleteTarget(emp); setDeleteError('') }}
                        className="p-1.5 rounded hover:bg-red-500/10 text-[--muted] hover:text-red-400 transition-colors">
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-[--border] bg-[--surface]">
          <span className="text-xs text-[--muted]">
            Page {page} of {totalPages}
          </span>
          <div className="flex items-center gap-1">
            <PagBtn onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
              <ChevronLeft size={14} />
            </PagBtn>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const p = Math.max(1, Math.min(page - 2 + i, totalPages - 4 + i))
              return (
                <PagBtn key={p} onClick={() => setPage(p)} active={p === page}>
                  {p}
                </PagBtn>
              )
            })}
            <PagBtn onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
              <ChevronRight size={14} />
            </PagBtn>
          </div>
        </div>
      </div>

      {/* Delete confirm */}
      {deleteTarget && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/60 backdrop-blur-sm">
          <div className="bg-[--surface] border border-[--border] rounded-xl p-6 max-w-sm w-full shadow-2xl">
            <div className="flex items-start gap-3 mb-4">
              <AlertCircle size={20} className="text-red-400 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-medium text-[--text] mb-1">Delete Employee</h3>
                <p className="text-sm text-[--muted]">Remove <strong className="text-[--text]">{deleteTarget.name}</strong>? This cannot be undone.</p>
              </div>
            </div>
            {deleteError && <p className="text-xs text-red-400 mb-3">{deleteError}</p>}
            <div className="flex gap-2 justify-end">
              <button onClick={() => setDeleteTarget(null)}
                className="px-4 py-2 text-sm rounded-lg border border-[--border] text-[--muted] hover:text-[--text] transition-colors">
                Cancel
              </button>
              <button onClick={() => deleteMut.mutate(deleteTarget.id)}
                disabled={deleteMut.isPending}
                className="px-4 py-2 text-sm rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors disabled:opacity-50">
                {deleteMut.isPending ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Employee modal */}
      {modal && <EmployeeModal mode={modal.mode} employee={modal.employee} onClose={() => setModal(null)} />}
    </div>
  )
}

function Select({ value, onChange, placeholder, children }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className="px-3 py-2 text-sm bg-[--surface] border border-[--border] rounded-lg text-[--text] focus:outline-none focus:border-[--teal] transition-colors cursor-pointer">
      <option value="">{placeholder}</option>
      {children}
    </select>
  )
}

function PagBtn({ onClick, disabled, active, children }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`min-w-[30px] h-7 px-2 rounded text-xs flex items-center justify-center transition-colors
        ${active ? 'bg-[--gold] text-[--bg] font-medium' : 'text-[--muted] hover:text-[--text] hover:bg-[--surface2]'}
        ${disabled ? 'opacity-30 cursor-not-allowed' : ''}`}>
      {children}
    </button>
  )
}
