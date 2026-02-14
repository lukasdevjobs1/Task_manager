"use client"

import { useState } from "react"
import useSWR, { mutate } from "swr"
import {
  Loader2,
  MapPin,
  Send,
  CheckCircle2,
} from "lucide-react"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

interface CreateTaskFormProps {
  onSuccess?: () => void
}

export function CreateTaskForm({ onSuccess }: CreateTaskFormProps) {
  const { data: usersData } = useSWR("/api/users", fetcher)
  const users = usersData?.users || []

  const [form, setForm] = useState({
    title: "",
    description: "",
    address: "",
    latitude: "",
    longitude: "",
    priority: "media",
    due_date: "",
    assigned_to: "",
    assignNow: false,
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState("")

  function parseGoogleMapsUrl(url: string) {
    // Try to parse coordinates from a Google Maps URL
    const match = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/)
    if (match) {
      setForm((f) => ({ ...f, latitude: match[1], longitude: match[2] }))
    }
    // Also try the q= format
    const qMatch = url.match(/q=(-?\d+\.\d+),(-?\d+\.\d+)/)
    if (qMatch) {
      setForm((f) => ({ ...f, latitude: qMatch[1], longitude: qMatch[2] }))
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const res = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: form.title,
          description: form.description || null,
          address: form.address || null,
          latitude: form.latitude ? parseFloat(form.latitude) : null,
          longitude: form.longitude ? parseFloat(form.longitude) : null,
          priority: form.priority,
          due_date: form.due_date || null,
          assigned_to: form.assignNow && form.assigned_to ? form.assigned_to : null,
        }),
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.error)

      setSuccess(true)
      setForm({
        title: "",
        description: "",
        address: "",
        latitude: "",
        longitude: "",
        priority: "media",
        due_date: "",
        assigned_to: "",
        assignNow: false,
      })
      mutate("/api/tasks?unassigned=true")
      mutate("/api/tasks")
      mutate("/api/dashboard/stats")

      setTimeout(() => {
        setSuccess(false)
        onSuccess?.()
      }, 1500)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar tarefa")
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-border bg-card py-16">
        <CheckCircle2 className="h-12 w-12 text-[var(--success)]" />
        <p className="text-lg font-semibold text-foreground">Tarefa criada com sucesso!</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-border bg-card p-6">
      <div className="grid gap-5 lg:grid-cols-2">
        {/* Title */}
        <div className="flex flex-col gap-1.5 lg:col-span-2">
          <label className="text-sm font-medium text-foreground">
            Titulo *
          </label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Ex: Instalacao fibra optica - Cliente #123"
            className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            required
          />
        </div>

        {/* Description */}
        <div className="flex flex-col gap-1.5 lg:col-span-2">
          <label className="text-sm font-medium text-foreground">
            Descricao
          </label>
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Detalhes da tarefa..."
            rows={3}
            className="rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        {/* Priority */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-foreground">
            Prioridade
          </label>
          <select
            value={form.priority}
            onChange={(e) => setForm({ ...form, priority: e.target.value })}
            className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="baixa">Baixa</option>
            <option value="media">Media</option>
            <option value="alta">Alta</option>
            <option value="urgente">Urgente</option>
          </select>
        </div>

        {/* Due date */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-foreground">
            Prazo
          </label>
          <input
            type="date"
            value={form.due_date}
            onChange={(e) => setForm({ ...form, due_date: e.target.value })}
            className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        {/* Address */}
        <div className="flex flex-col gap-1.5 lg:col-span-2">
          <label className="text-sm font-medium text-foreground">
            <MapPin className="mr-1 inline h-3.5 w-3.5" />
            Endereco / Local
          </label>
          <input
            type="text"
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            placeholder="Rua, numero, bairro"
            className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        {/* Google Maps URL parser */}
        <div className="flex flex-col gap-1.5 lg:col-span-2">
          <label className="text-sm font-medium text-foreground">
            Link Google Maps (para extrair coordenadas)
          </label>
          <input
            type="url"
            placeholder="Cole o link do Google Maps aqui"
            onChange={(e) => parseGoogleMapsUrl(e.target.value)}
            className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          {form.latitude && form.longitude && (
            <p className="text-xs text-[var(--success)]">
              Coordenadas: {form.latitude}, {form.longitude}
            </p>
          )}
        </div>

        {/* Assign toggle */}
        <div className="flex flex-col gap-3 lg:col-span-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.assignNow}
              onChange={(e) => setForm({ ...form, assignNow: e.target.checked })}
              className="h-4 w-4 rounded border-input accent-primary"
            />
            <span className="text-sm font-medium text-foreground">
              Atribuir a um colaborador agora
            </span>
          </label>

          {form.assignNow && (
            <select
              value={form.assigned_to}
              onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}
              className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              required={form.assignNow}
            >
              <option value="">Selecione um colaborador</option>
              {users
                .filter((u: { role: string }) => u.role === "user")
                .map((u: { id: number; full_name: string; team: string }) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name} ({u.team === "fusao" ? "Fusao" : "Infraestrutura"})
                  </option>
                ))}
            </select>
          )}
        </div>
      </div>

      {error && (
        <p className="mt-4 text-sm text-destructive">{error}</p>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          {form.assignNow ? "Criar e Atribuir" : "Criar na Caixa"}
        </button>
      </div>
    </form>
  )
}
