"use client"

import { cn } from "@/lib/utils"

interface PerformanceTableProps {
  userPerformance: Array<{
    id: number
    name: string
    team: string
    total: number
    completed: number
    inProgress: number
    pending: number
    rate: number
  }>
}

export function PerformanceTable({ userPerformance }: PerformanceTableProps) {
  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="p-4">
        <h3 className="text-sm font-semibold text-foreground">
          Desempenho dos Colaboradores
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-t border-border">
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">
                Colaborador
              </th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">
                Equipe
              </th>
              <th className="px-4 py-3 text-center font-medium text-muted-foreground">
                Total
              </th>
              <th className="px-4 py-3 text-center font-medium text-muted-foreground">
                Concluidas
              </th>
              <th className="px-4 py-3 text-center font-medium text-muted-foreground">
                Em Andamento
              </th>
              <th className="px-4 py-3 text-center font-medium text-muted-foreground">
                Pendentes
              </th>
              <th className="px-4 py-3 text-center font-medium text-muted-foreground">
                Taxa
              </th>
            </tr>
          </thead>
          <tbody>
            {userPerformance.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="px-4 py-8 text-center text-muted-foreground"
                >
                  Nenhum colaborador encontrado
                </td>
              </tr>
            ) : (
              userPerformance.map((user, i) => (
                <tr
                  key={user.id}
                  className="border-t border-border transition-colors hover:bg-muted/50"
                >
                  <td className="px-4 py-3 font-medium text-foreground">
                    <div className="flex items-center gap-2">
                      {i < 3 && (
                        <span
                          className={cn(
                            "flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold",
                            i === 0
                              ? "bg-[var(--chart-4)] text-[var(--warning-foreground)]"
                              : i === 1
                                ? "bg-muted text-muted-foreground"
                                : "bg-[var(--chart-5)]/20 text-[var(--chart-5)]"
                          )}
                        >
                          {i + 1}
                        </span>
                      )}
                      {user.name}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{user.team}</td>
                  <td className="px-4 py-3 text-center text-foreground">{user.total}</td>
                  <td className="px-4 py-3 text-center text-[var(--success)]">
                    {user.completed}
                  </td>
                  <td className="px-4 py-3 text-center text-[var(--chart-1)]">
                    {user.inProgress}
                  </td>
                  <td className="px-4 py-3 text-center text-[var(--chart-4)]">
                    {user.pending}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={cn(
                        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium",
                        user.rate >= 70
                          ? "bg-[var(--success)]/10 text-[var(--success)]"
                          : user.rate >= 40
                            ? "bg-[var(--chart-4)]/10 text-[var(--chart-4)]"
                            : "bg-destructive/10 text-destructive"
                      )}
                    >
                      {user.rate}%
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
