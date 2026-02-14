"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { formatDistanceToNow } from "date-fns"
import { ptBR } from "date-fns/locale"
import { ArrowRight } from "lucide-react"

interface RecentTasksProps {
  tasks: Array<{
    id: number
    title: string
    status: string
    priority: string
    created_at: string
    assigned_to_user: { full_name: string } | null
  }>
}

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
  urgente: { label: "Urgente", className: "text-destructive" },
}

export function RecentTasks({ tasks }: RecentTasksProps) {
  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between p-4">
        <h3 className="text-sm font-semibold text-foreground">
          Tarefas Recentes
        </h3>
        <Link
          href="/tasks"
          className="flex items-center gap-1 text-xs text-primary transition-colors hover:text-primary/80"
        >
          Ver todas
          <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="flex flex-col">
        {tasks.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-muted-foreground">
            Nenhuma tarefa encontrada
          </div>
        ) : (
          tasks.map((task) => {
            const status = STATUS_MAP[task.status] || STATUS_MAP.pendente
            const priority = PRIORITY_MAP[task.priority] || PRIORITY_MAP.media
            return (
              <Link
                key={task.id}
                href={`/tasks/${task.id}`}
                className="flex items-center justify-between border-t border-border px-4 py-3 transition-colors hover:bg-muted/50"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">
                    {task.title}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {task.assigned_to_user?.full_name || "Nao atribuida"} &middot;{" "}
                    {formatDistanceToNow(new Date(task.created_at), {
                      addSuffix: true,
                      locale: ptBR,
                    })}
                  </p>
                </div>
                <div className="ml-3 flex items-center gap-2">
                  <span className={cn("text-xs font-medium", priority.className)}>
                    {priority.label}
                  </span>
                  <span
                    className={cn(
                      "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium",
                      status.className
                    )}
                  >
                    {status.label}
                  </span>
                </div>
              </Link>
            )
          })
        )}
      </div>
    </div>
  )
}
