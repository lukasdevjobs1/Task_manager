"use client"

import { useState } from "react"
import useSWR, { mutate } from "swr"
import {
  Loader2,
  Plus,
  Building2,
  Users,
  ClipboardList,
  CheckCircle2,
  ToggleLeft,
  ToggleRight,
  Trash2,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useSession } from "@/hooks/use-session"
import { useRouter } from "next/navigation"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function AdminCompaniesPage() {
  const { user } = useSession()
  const router = useRouter()
  const { data, isLoading } = useSWR("/api/admin/companies", fetcher)
  const companies = data?.companies || []

  const [showCreate, setShowCreate] = useState(false)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [error, setError] = useState("")
  const [createForm, setCreateForm] = useState({
    name: "",
    slug: "",
    admin_username: "",
    admin_password: "",
    admin_full_name: "",
  })

  if (!user?.is_super_admin) {
    router.push("/dashboard")
    return null
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setActionLoading(-1)
    try {
      const res = await fetch("/api/admin/companies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createForm),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error)
      mutate("/api/admin/companies")
      setShowCreate(false)
      setCreateForm({ name: "", slug: "", admin_username: "", admin_password: "", admin_full_name: "" })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar empresa")
    } finally {
      setActionLoading(null)
    }
  }

  async function handleToggle(companyId: number) {
    setActionLoading(companyId)
    try {
      await fetch(`/api/admin/companies/${companyId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "toggle_status" }),
      })
      mutate("/api/admin/companies")
    } finally {
      setActionLoading(null)
    }
  }

  async function handleDelete(companyId: number, name: string) {
    const confirmation = prompt(
      `Para excluir "${name}", digite o nome da empresa:`
    )
    if (confirmation !== name) return
    setActionLoading(companyId)
    try {
      await fetch(`/api/admin/companies/${companyId}`, { method: "DELETE" })
      mutate("/api/admin/companies")
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

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{companies.length} empresas</p>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreate ? "Cancelar" : "Nova Empresa"}
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} className="rounded-xl border border-border bg-card p-6">
          <h3 className="mb-4 text-sm font-semibold text-foreground">Criar Nova Empresa</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Nome *</label>
              <input
                type="text"
                value={createForm.name}
                onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                placeholder="Nome da empresa"
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Slug * (ex: minha-empresa)</label>
              <input
                type="text"
                value={createForm.slug}
                onChange={(e) => setCreateForm({ ...createForm, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "") })}
                placeholder="slug-da-empresa"
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
                required
              />
            </div>
            <div className="sm:col-span-2">
              <p className="mb-2 text-xs font-medium text-muted-foreground">
                Administrador inicial (opcional)
              </p>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Nome completo do admin</label>
              <input
                type="text"
                value={createForm.admin_full_name}
                onChange={(e) => setCreateForm({ ...createForm, admin_full_name: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Usuario do admin</label>
              <input
                type="text"
                value={createForm.admin_username}
                onChange={(e) => setCreateForm({ ...createForm, admin_username: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Senha do admin</label>
              <input
                type="password"
                value={createForm.admin_password}
                onChange={(e) => setCreateForm({ ...createForm, admin_password: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
              />
            </div>
          </div>
          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              disabled={actionLoading === -1}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
            >
              {actionLoading === -1 && <Loader2 className="h-4 w-4 animate-spin" />}
              Criar Empresa
            </button>
          </div>
        </form>
      )}

      {/* Companies grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {companies.map(
          (c: {
            id: number
            name: string
            slug: string
            active: boolean
            userCount: number
            taskCount: number
            completedCount: number
          }) => (
            <div
              key={c.id}
              className={cn(
                "rounded-xl border bg-card p-5 transition-colors",
                c.active ? "border-border" : "border-destructive/30 opacity-60"
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                    <Building2 className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">{c.name}</h3>
                    <p className="text-xs text-muted-foreground">{c.slug}</p>
                  </div>
                </div>
                <span
                  className={cn(
                    "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium",
                    c.active
                      ? "bg-[var(--success)]/10 text-[var(--success)]"
                      : "bg-destructive/10 text-destructive"
                  )}
                >
                  {c.active ? "Ativa" : "Inativa"}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2">
                <div className="rounded-lg bg-muted/50 px-3 py-2 text-center">
                  <Users className="mx-auto h-3.5 w-3.5 text-muted-foreground" />
                  <p className="mt-1 text-sm font-bold text-foreground">{c.userCount}</p>
                  <p className="text-[10px] text-muted-foreground">Usuarios</p>
                </div>
                <div className="rounded-lg bg-muted/50 px-3 py-2 text-center">
                  <ClipboardList className="mx-auto h-3.5 w-3.5 text-muted-foreground" />
                  <p className="mt-1 text-sm font-bold text-foreground">{c.taskCount}</p>
                  <p className="text-[10px] text-muted-foreground">Tarefas</p>
                </div>
                <div className="rounded-lg bg-muted/50 px-3 py-2 text-center">
                  <CheckCircle2 className="mx-auto h-3.5 w-3.5 text-[var(--success)]" />
                  <p className="mt-1 text-sm font-bold text-foreground">{c.completedCount}</p>
                  <p className="text-[10px] text-muted-foreground">Concluidas</p>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-1 border-t border-border pt-3">
                <button
                  onClick={() => handleToggle(c.id)}
                  disabled={actionLoading === c.id}
                  className="flex items-center gap-1 rounded-md px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  {c.active ? <ToggleRight className="h-3.5 w-3.5 text-[var(--success)]" /> : <ToggleLeft className="h-3.5 w-3.5" />}
                  {c.active ? "Desativar" : "Ativar"}
                </button>
                <button
                  onClick={() => handleDelete(c.id, c.name)}
                  disabled={actionLoading === c.id}
                  className="ml-auto flex items-center gap-1 rounded-md px-2 py-1.5 text-xs text-destructive transition-colors hover:bg-destructive/10"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Excluir
                </button>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  )
}
