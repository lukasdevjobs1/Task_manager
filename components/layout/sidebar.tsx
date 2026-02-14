"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  LayoutDashboard,
  ClipboardList,
  CheckCircle2,
  Bell,
  Users,
  Building2,
  LogOut,
  Wifi,
  X,
  ChevronLeft,
} from "lucide-react"
import { cn } from "@/lib/utils"
import type { SessionUser } from "@/lib/auth"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

interface SidebarProps {
  user: SessionUser
  open: boolean
  onClose: () => void
}

export function Sidebar({ user, open, onClose }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()

  const { data: notifData } = useSWR(
    "/api/notifications/count",
    fetcher,
    { refreshInterval: 30000 }
  )
  const unreadCount = notifData?.count ?? 0

  const navItems = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      label: "Tarefas",
      href: "/tasks",
      icon: ClipboardList,
    },
    {
      label: "Concluidas",
      href: "/tasks/completed",
      icon: CheckCircle2,
    },
    {
      label: "Notificacoes",
      href: "/notifications",
      icon: Bell,
      badge: unreadCount > 0 ? unreadCount : undefined,
    },
  ]

  const adminItems = user.role === "admin"
    ? [
        {
          label: "Usuarios",
          href: "/admin/users",
          icon: Users,
        },
        ...(user.is_super_admin
          ? [
              {
                label: "Empresas",
                href: "/admin/companies",
                icon: Building2,
              },
            ]
          : []),
      ]
    : []

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" })
    router.push("/login")
    router.refresh()
  }

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-sidebar text-sidebar-foreground transition-transform duration-300 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between border-b border-sidebar-border px-4">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <Wifi className="h-4 w-4" />
            </div>
            <span className="text-sm font-semibold tracking-tight text-sidebar-foreground">
              Task Manager
            </span>
          </Link>
          <button
            onClick={onClose}
            className="rounded-md p-1.5 text-sidebar-foreground/60 transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground lg:hidden"
            aria-label="Fechar menu"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="sidebar-scrollbar flex-1 overflow-y-auto px-3 py-4">
          <div className="flex flex-col gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  {item.label}
                  {item.badge && (
                    <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-sidebar-primary px-1.5 text-[10px] font-bold text-sidebar-primary-foreground">
                      {item.badge > 99 ? "99+" : item.badge}
                    </span>
                  )}
                </Link>
              )
            })}
          </div>

          {adminItems.length > 0 && (
            <div className="mt-6">
              <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-sidebar-foreground/40">
                Administracao
              </p>
              <div className="flex flex-col gap-1">
                {adminItems.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={onClose}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-sidebar-accent text-sidebar-accent-foreground"
                          : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground"
                      )}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      {item.label}
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
        </nav>

        {/* User / footer */}
        <div className="border-t border-sidebar-border p-3">
          <div className="mb-2 rounded-lg bg-sidebar-accent/50 px-3 py-2.5">
            <p className="truncate text-sm font-medium text-sidebar-accent-foreground">
              {user.full_name}
            </p>
            <p className="truncate text-xs text-sidebar-foreground/50">
              {user.company_name} &middot;{" "}
              {user.role === "admin" ? "Gerente" : "Colaborador"}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground/70 transition-colors hover:bg-destructive/10 hover:text-destructive"
          >
            <LogOut className="h-4 w-4" />
            Sair
          </button>
        </div>
      </aside>
    </>
  )
}
