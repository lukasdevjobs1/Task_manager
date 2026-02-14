"use client"

import useSWR from "swr"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { TeamChart } from "@/components/dashboard/team-chart"
import { PerformanceTable } from "@/components/dashboard/performance-table"
import { RecentTasks } from "@/components/dashboard/recent-tasks"
import { Loader2 } from "lucide-react"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function DashboardPage() {
  const { data, isLoading } = useSWR("/api/dashboard/stats", fetcher, {
    refreshInterval: 60000,
  })

  if (isLoading || !data) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <StatsCards stats={data.stats} />
      <TeamChart
        teamStats={data.teamStats}
        statusDistribution={data.statusDistribution}
      />
      <div className="grid gap-4 xl:grid-cols-2">
        <PerformanceTable userPerformance={data.userPerformance} />
        <RecentTasks tasks={data.recentTasks} />
      </div>
    </div>
  )
}
