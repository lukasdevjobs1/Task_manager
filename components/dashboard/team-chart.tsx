"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"

interface TeamChartProps {
  teamStats: Array<{
    team: string
    total: number
    completed: number
    inProgress: number
    pending: number
  }>
  statusDistribution: Array<{
    name: string
    value: number
    fill: string
  }>
}

export function TeamChart({ teamStats, statusDistribution }: TeamChartProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {/* Bar chart - tasks by team */}
      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold text-foreground">
          Tarefas por Equipe
        </h3>
        {teamStats.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
            Nenhum dado disponivel
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={teamStats} barGap={2}>
              <XAxis
                dataKey="team"
                tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  color: "var(--foreground)",
                  fontSize: "12px",
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: "12px" }}
              />
              <Bar
                dataKey="completed"
                name="Concluidas"
                fill="var(--chart-2)"
                radius={[4, 4, 0, 0]}
                stackId="a"
              />
              <Bar
                dataKey="inProgress"
                name="Em andamento"
                fill="var(--chart-1)"
                radius={[0, 0, 0, 0]}
                stackId="a"
              />
              <Bar
                dataKey="pending"
                name="Pendentes"
                fill="var(--chart-4)"
                radius={[0, 0, 0, 0]}
                stackId="a"
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Pie chart - status distribution */}
      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold text-foreground">
          Distribuicao de Status
        </h3>
        {statusDistribution.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
            Nenhum dado disponivel
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={statusDistribution}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} (${(percent * 100).toFixed(0)}%)`
                }
                labelLine={{ stroke: "var(--muted-foreground)", strokeWidth: 1 }}
              >
                {statusDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  color: "var(--foreground)",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
