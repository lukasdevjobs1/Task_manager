"use client"

import { useState } from "react"
import { usePathname, useRouter } from "next/navigation"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { useSession } from "@/hooks/use-session"
import { Loader2 } from "lucide-react"

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/tasks": "Gestao de Tarefas",
  "/tasks/completed": "Tarefas Concluidas",
  "/notifications": "Notificacoes",
  "/admin/users": "Gerenciar Usuarios",
  "/admin/companies": "Gerenciar Empresas",
}

function getTitle(pathname: string) {
  if (pathname.startsWith("/tasks/") && pathname !== "/tasks/completed") {
    return "Detalhes da Tarefa"
  }
  return TITLES[pathname] || "Task Manager"
}

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const { user, isLoading } = useSession()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!user) {
    router.push("/login")
    return null
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar
        user={user}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header
          title={getTitle(pathname)}
          onMenuClick={() => setSidebarOpen(true)}
        />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
