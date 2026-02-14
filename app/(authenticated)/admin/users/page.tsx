"use client"

import { useState } from "react"
import useSWR, { mutate } from "swr"
import {
  Loader2,
  Plus,
  Key,
  Trash2,
  ToggleLeft,
  ToggleRight,
  X,
  UserPlus,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function AdminUsersPage() {
  const { data, isLoading } = useSWR("/api/admin/users", fetcher)
  const users = data?.users || []

  const [showCreate, setShowCreate] = useState(false)
  const [changePasswordId, setChangePasswordId] = useState<number | null>(null)
  const [newPassword, setNewPassword] = useState("")
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [error, setError] = useState("")

  // Create form
  const [createForm, setCreateForm] = useState({
    username: "",
    password: "",
    full_name: "",
    team: "fusao",
    role: "user",
  })

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setActionLoading(-1)
    try {
      const res = await fetch("/api/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createForm),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error)
      mutate("/api/admin/users")
      setShowCreate(false)
      setCreateForm({ username: "", password: "", full_name: "", team: "fusao", role: "user" })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar usuario")
    } finally {
      setActionLoading(null)
    }
  }

  async function handleToggleStatus(userId: number) {
    setActionLoading(userId)
    try {
      await fetch(`/api/admin/users/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "toggle_status" }),
      })
      mutate("/api/admin/users")
    } finally {
      setActionLoading(null)
    }
  }

  async function handleChangePassword(userId: number) {
    if (!newPassword || newPassword.length < 6) {
      setError("Senha deve ter no minimo 6 caracteres")
      return
    }
    setActionLoading(userId)
    try {
      await fetch(`/api/admin/users/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "change_password", password: newPassword }),
      })
      setChangePasswordId(null)
      setNewPassword("")
    } catch {
      setError("Erro ao alterar senha")
    } finally {
      setActionLoading(null)
    }
  }

  async function handleDelete(userId: number, name: string) {
    if (!confirm(`Excluir usuario "${name}" permanentemente?`)) return
    setActionLoading(userId)
    try {
      await fetch(`/api/admin/users/${userId}`, { method: "DELETE" })
      mutate("/api/admin/users")
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
        <p className="text-sm text-muted-foreground">{users.length} usuarios</p>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          {showCreate ? <X className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
          {showCreate ? "Cancelar" : "Novo Usuario"}
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <form
          onSubmit={handleCreate}
          className="rounded-xl border border-border bg-card p-6"
        >
          <h3 className="mb-4 text-sm font-semibold text-foreground">
            Criar Novo Usuario
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Nome completo *
              </label>
              <input
                type="text"
                value={createForm.full_name}
                onChange={(e) => setCreateForm({ ...createForm, full_name: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Usuario *
              </label>
              <input
                type="text"
                value={createForm.username}
                onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Senha * (min. 6 caracteres)
              </label>
              <input
                type="password"
                value={createForm.password}
                onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
                required
                minLength={6}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Equipe
              </label>
              <select
                value={createForm.team}
                onChange={(e) => setCreateForm({ ...createForm, team: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
              >
                <option value="fusao">Fusao</option>
                <option value="infraestrutura">Infraestrutura</option>
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">
                Perfil
              </label>
              <select
                value={createForm.role}
                onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                className="h-9 rounded-lg border border-input bg-background px-3 text-sm text-foreground"
              >
                <option value="user">Colaborador</option>
                <option value="admin">Gerente (Admin)</option>
              </select>
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
              Criar Usuario
            </button>
          </div>
        </form>
      )}

      {/* Users table */}
      <div className="rounded-xl border border-border bg-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Nome</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Usuario</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Equipe</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Perfil</th>
                <th className="px-4 py-3 text-center font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Criado em</th>
                <th className="px-4 py-3 text-right font-medium text-muted-foreground">Acoes</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u: { id: number; username: string; full_name: string; team: string; role: string; active: boolean; created_at: string; is_super_admin: boolean }) => (
                <tr key={u.id} className="border-t border-border transition-colors hover:bg-muted/50">
                  <td className="px-4 py-3 font-medium text-foreground">
                    {u.full_name}
                    {u.is_super_admin && (
                      <span className="ml-1.5 inline-flex rounded-full bg-primary/10 px-1.5 py-0.5 text-[9px] font-bold text-primary">
                        SUPER
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{u.username}</td>
                  <td className="px-4 py-3 text-muted-foreground capitalize">{u.team}</td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium",
                        u.role === "admin"
                          ? "bg-primary/10 text-primary"
                          : "bg-muted text-muted-foreground"
                      )}
                    >
                      {u.role === "admin" ? "Gerente" : "Colaborador"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={cn(
                        "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium",
                        u.active
                          ? "bg-[var(--success)]/10 text-[var(--success)]"
                          : "bg-destructive/10 text-destructive"
                      )}
                    >
                      {u.active ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {format(new Date(u.created_at), "dd/MM/yyyy", { locale: ptBR })}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => handleToggleStatus(u.id)}
                        disabled={actionLoading === u.id}
                        className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                        title={u.active ? "Desativar" : "Ativar"}
                      >
                        {u.active ? <ToggleRight className="h-4 w-4 text-[var(--success)]" /> : <ToggleLeft className="h-4 w-4" />}
                      </button>
                      <button
                        onClick={() => {
                          setChangePasswordId(changePasswordId === u.id ? null : u.id)
                          setNewPassword("")
                        }}
                        className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                        title="Alterar senha"
                      >
                        <Key className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(u.id, u.full_name)}
                        disabled={actionLoading === u.id}
                        className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                        title="Excluir"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    {changePasswordId === u.id && (
                      <div className="mt-2 flex items-center gap-2">
                        <input
                          type="password"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Nova senha (min. 6)"
                          className="h-8 flex-1 rounded-md border border-input bg-background px-2 text-xs text-foreground"
                        />
                        <button
                          onClick={() => handleChangePassword(u.id)}
                          disabled={actionLoading === u.id}
                          className="h-8 rounded-md bg-primary px-3 text-xs font-medium text-primary-foreground"
                        >
                          Salvar
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
