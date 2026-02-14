"use client"

import { useState } from "react"
import useSWR from "swr"
import Link from "next/link"
import {
  Loader2,
  Search,
  ExternalLink,
  MapPin,
  Calendar,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

const STATUS_MAP: Record<string, { label: string; className: string }> = {
  pendente: {
    label: "Pendente",
    className: "bg-[var(--chart-4)]/10 text-[var(--chart-4)]",
  },
  em_andamento: {
    label: "Em andamento",
    className: "bg-[var(--chart-1)]/10 text-[var(--chart-1)]",
  },
  concluida: {
    label: "Concluida",
    className: "bg-[var(--success)]/10 text-[var(--success)]",
  },
}

const PRIORITY_MAP: Record<string, { label: string; className: string }> = {
  baixa: { label: "Baixa", className: "text-muted-foreground" },
  media: { label: "Media", className: "text-[var(--chart-1)]" },
  alta: { label: "Alta", className: "text-[var(--chart-4)]" },
  urgente: { label: "Urgente", className: "text-destructive font-semibold" },
}

export function AssignedTasks() {
  const [statusFilter, setStatusFilter] = useState("")
  const [searchQuery, setSearchQuery] = useState("")

  const url = statusFilter
    ? `/api/tasks?status=${statusFilter}`
    : "/api/tasks"
  const { data, isLoading } = useSWR(url, fetcher)

  const allTasks = data?.tasks || []
  // Filter only assigned tasks and by search
  const tasks = allTasks
    .filter((t: { assigned_to: number | null }) => t.assigned_to !== null)
    .filter((t: { title: string; assigned_to_user: { full_name: string } | null }) =>
      searchQuery === ""
        ? true
        : t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.assigned_to_user?.full_name?.toLowerCase().includes(searchQuery.toLowerCase())
    )

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar por titulo ou colaborador..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
        >
          <option value="">Todos os status</option>
          <option value="pendente">Pendente</option>
          <option value="em_andamento">Em andamento</option>
          <option value="concluida">Concluida</option>
        </select>
      </div>

      {/* Tasks list */}
      {tasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-border bg-card py-16">
          <p className="text-sm text-muted-foreground">Nenhuma tarefa encontrada</p>
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {tasks.map(
            (task: {
              id: number
              title: string
              status: string
              priority: string
              address: string | null
              due_date: string | null
              created_at: string
              assigned_to_user: { full_name: string; team: string } | null
            }) => {
              const status = STATUS_MAP[task.status] || STATUS_MAP.pendente
              const priority = PRIORITY_MAP[task.priority] || PRIORITY_MAP.media

              return (
                <Link
                  key={task.id}
                  href={`/tasks/${task.id}`}
                  className="group flex flex-col rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/30"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-sm font-medium text-foreground group-hover:text-primary">
                      {task.title}
                    </h4>
                    <ExternalLink className="h-3.5 w-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>

                  <div className="mt-2 flex items-center gap-2">
                    <span
                      className={cn(
                        "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium",
                        status.className
                      )}
                    >
                      {status.label}
                    </span>
                    <span className={cn("text-[10px] font-medium", priority.className)}>
                      {priority.label}
                    </span>
                  </div>

                  <div className="mt-3 flex flex-col gap-1">
                    <p className="text-xs text-muted-foreground">
                      {task.assigned_to_user?.full_name || "Nao atribuida"}
                    </p>
                    {task.address && (
                      <p className="flex items-center gap-1 text-xs text-muted-foreground">
                        <MapPin className="h-3 w-3" />
                        <span className="truncate">{task.address}</span>
                      </p>
                    )}
                    {task.due_date && (
                      <p className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        {format(new Date(task.due_date), "dd/MM/yyyy", { locale: ptBR })}
                      </p>
                    )}
                  </div>
                </Link>
              )
            }
          )}
        </div>
      )}
    </div>
  )
}
