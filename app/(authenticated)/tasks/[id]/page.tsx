"use client"

import { use } from "react"
import useSWR, { mutate } from "swr"
import { useRouter } from "next/navigation"
import { useState } from "react"
import {
  Loader2,
  ArrowLeft,
  MapPin,
  Calendar,
  User,
  Clock,
  Trash2,
  UserPlus,
  ImageIcon,
} from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"
import { useSession } from "@/hooks/use-session"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

const STATUS_MAP: Record<string, { label: string; className: string }> = {
  pendente: { label: "Pendente", className: "bg-[var(--chart-4)]/10 text-[var(--chart-4)]" },
  em_andamento: { label: "Em andamento", className: "bg-[var(--chart-1)]/10 text-[var(--chart-1)]" },
  concluida: { label: "Concluida", className: "bg-[var(--success)]/10 text-[var(--success)]" },
}

const PRIORITY_MAP: Record<string, { label: string; className: string }> = {
  baixa: { label: "Baixa", className: "text-muted-foreground" },
  media: { label: "Media", className: "text-[var(--chart-1)]" },
  alta: { label: "Alta", className: "text-[var(--chart-4)]" },
  urgente: { label: "Urgente", className: "text-destructive" },
}

export default function TaskDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const router = useRouter()
  const { user } = useSession()
  const isAdmin = user?.role === "admin"
  const { data, isLoading } = useSWR(`/api/tasks/${id}`, fetcher)
  const { data: usersData } = useSWR("/api/users", fetcher)
  const users = usersData?.users?.filter((u: { role: string }) => u.role === "user") || []

  const [reassigning, setReassigning] = useState(false)
  const [selectedUser, setSelectedUser] = useState("")
  const [actionLoading, setActionLoading] = useState(false)

  if (isLoading || !data) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const task = data.task
  const photos = data.photos || []
  const status = STATUS_MAP[task.status] || STATUS_MAP.pendente
  const priority = PRIORITY_MAP[task.priority] || PRIORITY_MAP.media

  async function handleReassign() {
    if (!selectedUser) return
    setActionLoading(true)
    try {
      await fetch(`/api/tasks/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assigned_to: parseInt(selectedUser) }),
      })
      mutate(`/api/tasks/${id}`)
      mutate("/api/tasks")
      setReassigning(false)
      setSelectedUser("")
    } finally {
      setActionLoading(false)
    }
  }

  async function handleDelete() {
    if (!confirm("Tem certeza que deseja excluir esta tarefa permanentemente?")) return
    setActionLoading(true)
    try {
      await fetch(`/api/tasks/${id}`, { method: "DELETE" })
      router.push("/tasks")
    } finally {
      setActionLoading(false)
    }
  }

  async function handleUnassign() {
    setActionLoading(true)
    try {
      await fetch(`/api/tasks/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assigned_to: null }),
      })
      mutate(`/api/tasks/${id}`)
      mutate("/api/tasks")
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      {/* Back button */}
      <Link
        href="/tasks"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar
      </Link>

      <div className="flex flex-col gap-6">
        {/* Main info card */}
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex-1">
              <h2 className="text-xl font-bold text-foreground">{task.title}</h2>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <span className={cn("inline-flex rounded-full px-2.5 py-1 text-xs font-medium", status.className)}>
                  {status.label}
                </span>
                <span className={cn("text-xs font-medium", priority.className)}>
                  Prioridade: {priority.label}
                </span>
              </div>
            </div>

            {isAdmin && (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setReassigning(!reassigning)}
                  className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs font-medium text-foreground transition-colors hover:bg-muted"
                >
                  <UserPlus className="h-3.5 w-3.5" />
                  {task.assigned_to ? "Reatribuir" : "Atribuir"}
                </button>
                {task.assigned_to && (
                  <button
                    onClick={handleUnassign}
                    disabled={actionLoading}
                    className="rounded-lg border border-border px-3 py-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted"
                  >
                    Devolver a caixa
                  </button>
                )}
                <button
                  onClick={handleDelete}
                  disabled={actionLoading}
                  className="flex items-center gap-1.5 rounded-lg border border-destructive/30 px-3 py-2 text-xs font-medium text-destructive transition-colors hover:bg-destructive/10"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Excluir
                </button>
              </div>
            )}
          </div>

          {/* Reassign dialog */}
          {reassigning && isAdmin && (
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-border bg-muted/50 p-3">
              <select
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
                className="h-9 flex-1 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
              >
                <option value="">Selecione um colaborador</option>
                {users.map((u: { id: number; full_name: string }) => (
                  <option key={u.id} value={u.id}>{u.full_name}</option>
                ))}
              </select>
              <button
                onClick={handleReassign}
                disabled={!selectedUser || actionLoading}
                className="h-9 rounded-lg bg-primary px-4 text-xs font-medium text-primary-foreground disabled:opacity-50"
              >
                Confirmar
              </button>
            </div>
          )}

          {/* Details */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {task.description && (
              <div className="sm:col-span-2">
                <p className="text-xs font-medium text-muted-foreground">Descricao</p>
                <p className="mt-1 text-sm text-foreground">{task.description}</p>
              </div>
            )}

            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Atribuido a</p>
                <p className="text-sm font-medium text-foreground">
                  {task.assigned_to_user?.full_name || "Nao atribuida"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Criado por</p>
                <p className="text-sm font-medium text-foreground">
                  {task.assigned_by_user?.full_name || "-"}
                </p>
              </div>
            </div>

            {task.address && (
              <div className="flex items-center gap-2 sm:col-span-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Endereco</p>
                  <p className="text-sm font-medium text-foreground">{task.address}</p>
                </div>
              </div>
            )}

            {task.due_date && (
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Prazo</p>
                  <p className="text-sm font-medium text-foreground">
                    {format(new Date(task.due_date), "dd/MM/yyyy", { locale: ptBR })}
                  </p>
                </div>
              </div>
            )}

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Criado em</p>
                <p className="text-sm font-medium text-foreground">
                  {format(new Date(task.created_at), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                </p>
              </div>
            </div>
          </div>

          {/* Observations (field notes) */}
          {task.observations && (
            <div className="mt-6 rounded-lg border border-border bg-muted/30 p-4">
              <p className="text-xs font-medium text-muted-foreground">Observacoes do campo</p>
              <p className="mt-1 text-sm text-foreground">{task.observations}</p>
            </div>
          )}
        </div>

        {/* Map embed */}
        {task.latitude && task.longitude && (
          <div className="rounded-xl border border-border bg-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-foreground">Localizacao</h3>
            <div className="h-64 overflow-hidden rounded-lg">
              <iframe
                title="Mapa da tarefa"
                src={`https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d1000!2d${task.longitude}!3d${task.latitude}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sbr`}
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>
          </div>
        )}

        {/* Photos */}
        {photos.length > 0 && (
          <div className="rounded-xl border border-border bg-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-foreground">
              <ImageIcon className="mr-1.5 inline h-4 w-4" />
              Fotos ({photos.length})
            </h3>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {photos.map((photo: { id: number; photo_url: string; original_name: string }) => (
                <a
                  key={photo.id}
                  href={photo.photo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative aspect-square overflow-hidden rounded-lg bg-muted"
                >
                  <img
                    src={photo.photo_url}
                    alt={photo.original_name}
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                    crossOrigin="anonymous"
                  />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
