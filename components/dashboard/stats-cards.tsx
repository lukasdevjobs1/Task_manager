"use client"

import {
  ClipboardList,
  Clock,
  Activity,
  CheckCircle2,
  Inbox,
  AlertTriangle,
  Users,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface StatsCardsProps {
  stats: {
    total: number
    pending: number
    inProgress: number
    completed: number
    unassigned: number
    urgent: number
    high: number
    activeUsers: number
  }
}

const cards = [
  {
    label: "Total de Tarefas",
    key: "total" as const,
    icon: ClipboardList,
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    label: "Pendentes",
    key: "pending" as const,
    icon: Clock,
    color: "text-[var(--chart-4)]",
    bg: "bg-[var(--chart-4)]/10",
  },
  {
    label: "Em Andamento",
    key: "inProgress" as const,
    icon: Activity,
    color: "text-[var(--chart-1)]",
    bg: "bg-[var(--chart-1)]/10",
  },
  {
    label: "Concluidas",
    key: "completed" as const,
    icon: CheckCircle2,
    color: "text-[var(--success)]",
    bg: "bg-[var(--success)]/10",
  },
  {
    label: "Na Caixa",
    key: "unassigned" as const,
    icon: Inbox,
    color: "text-muted-foreground",
    bg: "bg-muted",
  },
  {
    label: "Urgentes",
    key: "urgent" as const,
    icon: AlertTriangle,
    color: "text-destructive",
    bg: "bg-destructive/10",
  },
]

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
      {cards.map((card) => (
        <div
          key={card.key}
          className="rounded-xl border border-border bg-card p-4"
        >
          <div className="flex items-center gap-2">
            <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg", card.bg)}>
              <card.icon className={cn("h-4 w-4", card.color)} />
            </div>
          </div>
          <p className="mt-3 text-2xl font-bold tracking-tight text-foreground">
            {stats[card.key]}
          </p>
          <p className="text-xs text-muted-foreground">{card.label}</p>
        </div>
      ))}
    </div>
  )
}
