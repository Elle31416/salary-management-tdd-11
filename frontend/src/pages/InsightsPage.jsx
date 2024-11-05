import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import {
  fetchSummary, fetchSalaryByCountry, fetchDistribution,
  fetchTopPaidTitles, fetchHeadcountByDept
} from '../lib/api'
import { formatSalary, formatNumber } from '../lib/utils'
import { Users, DollarSign, Globe, Building2, TrendingUp } from 'lucide-react'

const PIE_COLORS = ['#F4C842', '#2DD4BF', '#818CF8', '#F472B6', '#34D399', '#FB923C', '#60A5FA', '#A78BFA']

export default function InsightsPage() {
  const { data: summary } = useQuery({ queryKey: ['summary'], queryFn: fetchSummary })
  const { data: byCountry } = useQuery({ queryKey: ['salary-by-country'], queryFn: fetchSalaryByCountry })
  const { data: distribution } = useQuery({ queryKey: ['distribution'], queryFn: fetchDistribution })
  const { data: topTitles } = useQuery({ queryKey: ['top-titles'], queryFn: fetchTopPaidTitles })
  const { data: headcount } = useQuery({ queryKey: ['headcount'], queryFn: fetchHeadcountByDept })

  // Aggregate department headcount
  const deptData = headcount?.reduce((acc, { department, headcount: hc }) => {
    const found = acc.find(d => d.department === department)
    if (found) found.headcount += hc
    else acc.push({ department, headcount: hc })
    return acc
  }, []).sort((a, b) => b.headcount - a.headcount) || []

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-2xl text-[--text]">Compensation Insights</h1>
        <p className="text-sm text-[--muted] mt-0.5">Real-time analytics across your workforce</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: 'Total Employees', value: formatNumber(summary?.total_employees ?? 0), icon: Users, accent: '--teal' },
          { label: 'Active', value: formatNumber(summary?.active_employees ?? 0), icon: TrendingUp, accent: '--gold' },
          { label: 'Avg Salary', value: formatSalary(summary?.avg_salary ?? 0), icon: DollarSign, accent: '--gold' },
          { label: 'Countries', value: summary?.countries ?? 0, icon: Globe, accent: '--teal' },
          { label: 'Departments', value: summary?.departments ?? 0, icon: Building2, accent: '--teal' },
        ].map(({ label, value, icon: Icon, accent }) => (
          <div key={label} className="bg-[--surface] border border-[--border] rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-[--muted] uppercase tracking-wider">{label}</span>
              <Icon size={14} style={{ color: `var(${accent})` }} />
            </div>
            <div className="font-display text-2xl text-[--text]">{value}</div>
          </div>
        ))}
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Avg salary by country */}
        <ChartCard title="Average Salary by Country">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={byCountry?.sort((a, b) => b.avg - a.avg)} margin={{ left: 0 }}>
              <XAxis dataKey="country" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} width={50} />
              <Tooltip
                contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8 }}
                labelStyle={{ color: 'var(--text)' }}
                formatter={v => [formatSalary(v), 'Avg']}
              />
              <Bar dataKey="avg" fill="var(--gold)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Salary distribution */}
        <ChartCard title="Salary Distribution">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={distribution} margin={{ left: 0 }}>
              <XAxis dataKey="bucket" tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tickFormatter={v => formatNumber(v)} tick={{ fill: 'var(--muted)', fontSize: 11 }} axisLine={false} tickLine={false} width={55} />
              <Tooltip
                contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8 }}
                labelStyle={{ color: 'var(--text)' }}
                formatter={v => [formatNumber(v), 'Employees']}
              />
              <Bar dataKey="count" fill="var(--teal)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top paid titles */}
        <ChartCard title="Top 10 Highest-Paid Job Titles">
          <div className="space-y-2 mt-1">
            {topTitles?.map((t, i) => (
              <div key={t.job_title} className="flex items-center gap-3">
                <span className="text-xs font-mono-code text-[--muted] w-4 text-right">{i + 1}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-[--text]">{t.job_title}</span>
                    <span className="text-sm font-mono-code text-[--gold]">{formatSalary(t.avg_salary)}</span>
                  </div>
                  <div className="h-1.5 bg-[--surface2] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${(t.avg_salary / (topTitles[0]?.avg_salary || 1)) * 100}%`,
                        background: `hsl(${50 - i * 4}, 85%, ${60 - i * 2}%)`
                      }} />
                  </div>
                </div>
                <span className="text-xs text-[--muted] w-12 text-right">{formatNumber(t.headcount)}</span>
              </div>
            ))}
          </div>
        </ChartCard>

        {/* Department headcount pie */}
        <ChartCard title="Headcount by Department">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={deptData} dataKey="headcount" nameKey="department"
                cx="40%" cy="50%" outerRadius={100} innerRadius={55}
                paddingAngle={2}>
                {deptData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Legend
                iconType="circle" iconSize={8}
                formatter={(v) => <span style={{ color: 'var(--muted)', fontSize: 11 }}>{v}</span>}
              />
              <Tooltip
                contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8 }}
                formatter={v => [formatNumber(v), 'Employees']}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Country stats table */}
      <ChartCard title="Salary Stats by Country">
        <div className="overflow-x-auto mt-2">
          <table className="w-full text-sm">
            <thead>
              <tr>
                {['Country', 'Headcount', 'Min Salary', 'Avg Salary', 'Max Salary'].map(h => (
                  <th key={h} className="text-left text-xs text-[--muted] uppercase tracking-wider pb-3 font-medium pr-6">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {byCountry?.sort((a, b) => b.avg - a.avg).map(row => (
                <tr key={row.country} className="border-t border-[--border]">
                  <td className="py-3 pr-6 font-medium text-[--text]">{row.country}</td>
                  <td className="py-3 pr-6 text-[--muted] font-mono-code">{formatNumber(row.headcount)}</td>
                  <td className="py-3 pr-6 text-[--muted] font-mono-code">{formatSalary(row.min)}</td>
                  <td className="py-3 pr-6 text-[--gold] font-mono-code font-medium">{formatSalary(row.avg)}</td>
                  <td className="py-3 pr-6 text-[--muted] font-mono-code">{formatSalary(row.max)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ChartCard>
    </div>
  )
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-[--surface] border border-[--border] rounded-xl p-5">
      <h3 className="text-sm font-medium text-[--text] mb-4">{title}</h3>
      {children}
    </div>
  )
}
