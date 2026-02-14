"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { CreateTaskForm } from "@/components/tasks/create-task-form"
import { TaskInbox } from "@/components/tasks/task-inbox"
import { AssignedTasks } from "@/components/tasks/assigned-tasks"
import { PlusCircle, Inbox, ClipboardList } from "lucide-react"
import { useSession } from "@/hooks/use-session"

const TABS = [
  { id: "create", label: "Criar Tarefa", icon: PlusCircle },
  { id: "inbox", label: "Caixa da Empresa", icon: Inbox },
  { id: "assigned", label: "Tarefas Atribuidas", icon: ClipboardList },
] as const

type TabId = (typeof TABS)[number]["id"]

export default function TasksPage() {
  const [activeTab, setActiveTab] = useState<TabId>("assigned")
  const { user } = useSession()
  const isAdmin = user?.role === "admin"

  return (
    <div className="flex flex-col gap-6">
      {/* Tab navigation */}
      <div className="flex gap-1 rounded-lg border border-border bg-card p-1">
        {TABS.map((tab) => {
          if (tab.id === "create" && !isAdmin) return null
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <tab.icon className="h-4 w-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      {activeTab === "create" && isAdmin && <CreateTaskForm onSuccess={() => setActiveTab("assigned")} />}
      {activeTab === "inbox" && <TaskInbox />}
      {activeTab === "assigned" && <AssignedTasks />}
    </div>
  )
}
