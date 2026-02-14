"use client"

import { useState } from "react"
import useSWR, { mutate } from "swr"
import { Loader2, UserPlus, Trash2, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react"
import { cn } from "@/lib/utils"
import { formatDistanceToNow } from "date-fns"
import { ptBR } from "date-fns/locale"
import { useSession } from "@/hooks/use-session"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

const PRIORITY_MAP: Record<string, { label: string; className: string }> = {
  baixa: { label: "Baixa", className: "border-muted-foreground/30 text-muted-foreground" },
  media: { label: "Media", className: "border-[var(--chart-1)]/30 text-[var(--chart-1)]" },
  alta: { label: "Alta", className: "border-[var(--chart-4)]/30 text-[var(--chart-4)]" },
  urgente: { label: "Urgente", className: "border-destructive/30 text-destructive" },
}

export function TaskInbox() {
  const { user } = useSession()
  const isAdmin = user?.role === "admin"
  const { data, isLoading } = useSWR("/api/tasks?unassigned=true", fetcher)
  const { data: usersData } = useSWR("/api/users", fetcher)
  const tasks = data?.tasks || []
  const users = usersData?.users?.filter((u: { role: string }) => u.role === "user") || []

  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [assigningId, setAssigningId] = useState<number | null>(null)
  const [selectedUser, setSelectedUser] = useState("")
  const [actionLoading, setActionLoading] = useState<number | null>(null)

  async function handleAssign(taskId: number) {
    if (!selectedUser) return
    setActionLoading(taskId)
    try {
      await fetch(`/api/tasks/${taskId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assigned_to: parseInt(selectedUser) }),
      })
      mutate("/api/tasks?unassigned=true")
      mutate("/api/tasks")
      mutate("/api/dashboard/stats")
      setAssigningId(null)
      setSelectedUser("")
    } catch {
      // handle error silently
    } finally {
      setActionLoading(null)
    }
  }

  async function handleDelete(taskId: number) {
    if (!confirm("Tem certeza que deseja excluir esta tarefa?")) return
    setActionLoading(taskId)
    try {
      await fetch(`/api/tasks/${taskId}`, { method: "DELETE" })
      mutate("/api/tasks?unassigned=true")
      mutate("/api/dashboard/stats")
    } finally {
      setActionLoading(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-border bg-card py-16">
        <p className="text-sm text-muted-foreground">A caixa da empresa esta vazia</p>
        <p className="text-xs text-muted-foreground">
          Crie tarefas sem atribuir para que aparecam aqui
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {tasks.map((task: { id: number; title: string; description: string | null; priority: string; address: string | null; created_at: string }) => {
        const priority = PRIORITY_MAP[task.priority] || PRIORITY_MAP.media
        const isExpanded = expandedId === task.id
        const isAssigning = assigningId === task.id

        return (
          <div key={task.id} className="rounded-xl border border-border bg-card">
            <div
              className="flex cursor-pointer items-center justify-between p-4"
              onClick={() => setExpandedId(isExpanded ? null : task.id)}
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "inline-flex rounded-full border px-2 py-0.5 text-[10px] font-medium",
                      priority.className
                    )}
                  >
                    {priority.label}
                  </span>
                  <h4 className="truncate text-sm font-medium text-foreground">
                    {task.title}
                  </h4>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(task.created_at), {
                    addSuffix: true,
                    locale: ptBR,
                  })}
                </p>
              </div>
              {isExpanded ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )}
            </div>

            {isExpanded && (
              <div className="border-t border-border px-4 pb-4 pt-3">
                {task.description && (
                  <p className="mb-3 text-sm text-muted-foreground">{task.description}</p>
                )}
                {task.address && (
                  <p className="mb-3 text-xs text-muted-foreground">
                    Endereco: {task.address}
                  </p>
                )}

                {isAdmin && (
                  <div className="flex flex-wrap items-center gap-2">
                    {isAssigning ? (
                      <div className="flex flex-1 items-center gap-2">
                        <select
                          value={selectedUser}
                          onChange={(e) => setSelectedUser(e.target.value)}
                          className="h-9 flex-1 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
                        >
                          <option value="">Selecione...</option>
                          {users.map((u: { id: number; full_name: string }) => (
                            <option key={u.id} value={u.id}>
                              {u.full_name}
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={() => handleAssign(task.id)}
                          disabled={!selectedUser || actionLoading === task.id}
                          className="flex h-9 items-center gap-1 rounded-lg bg-primary px-3 text-xs font-medium text-primary-foreground disabled:opacity-50"
                        >
                          {actionLoading === task.id ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            "Atribuir"
                          )}
                        </button>
                        <button
                          onClick={() => setAssigningId(null)}
                          className="h-9 rounded-lg border border-border px-3 text-xs font-medium text-muted-foreground hover:bg-muted"
                        >
                          Cancelar
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => setAssigningId(task.id)}
                          className="flex items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                        >
                          <UserPlus className="h-3.5 w-3.5" />
                          Atribuir
                        </button>
                        <button
                          onClick={() => handleDelete(task.id)}
                          disabled={actionLoading === task.id}
                          className="flex items-center gap-1.5 rounded-lg border border-destructive/30 px-3 py-2 text-xs font-medium text-destructive transition-colors hover:bg-destructive/10"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          Excluir
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
