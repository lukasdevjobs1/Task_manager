import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()
  const companyId = session.company_id

  try {
    // Get all task_assignments for this company
    const { data: tasks, error: tasksError } = await supabase
      .from("task_assignments")
      .select("id, status, priority, assigned_to, assigned_by, created_at, updated_at, due_date")
      .eq("company_id", companyId)

    if (tasksError) throw tasksError

    // Get all users for this company
    const { data: users, error: usersError } = await supabase
      .from("users")
      .select("id, full_name, team, role, active")
      .eq("company_id", companyId)

    if (usersError) throw usersError

    const allTasks = tasks || []
    const allUsers = users || []

    // Overall stats
    const total = allTasks.length
    const pending = allTasks.filter((t) => t.status === "pendente").length
    const inProgress = allTasks.filter((t) => t.status === "em_andamento").length
    const completed = allTasks.filter((t) => t.status === "concluida").length
    const unassigned = allTasks.filter((t) => !t.assigned_to).length

    // By priority
    const urgent = allTasks.filter((t) => t.priority === "urgente").length
    const high = allTasks.filter((t) => t.priority === "alta").length

    // Team stats
    const teamMap = new Map<string, { total: number; completed: number; inProgress: number; pending: number }>()
    for (const task of allTasks) {
      if (!task.assigned_to) continue
      const user = allUsers.find((u) => u.id === task.assigned_to)
      if (!user) continue
      const team = user.team || "sem_equipe"
      const entry = teamMap.get(team) || { total: 0, completed: 0, inProgress: 0, pending: 0 }
      entry.total++
      if (task.status === "concluida") entry.completed++
      else if (task.status === "em_andamento") entry.inProgress++
      else entry.pending++
      teamMap.set(team, entry)
    }

    const teamStats = Array.from(teamMap.entries()).map(([team, stats]) => ({
      team: team === "fusao" ? "Fusao" : team === "infraestrutura" ? "Infraestrutura" : team,
      ...stats,
    }))

    // User performance
    const userPerformance = allUsers
      .filter((u) => u.role === "user" && u.active)
      .map((u) => {
        const userTasks = allTasks.filter((t) => t.assigned_to === u.id)
        const userCompleted = userTasks.filter((t) => t.status === "concluida").length
        return {
          id: u.id,
          name: u.full_name,
          team: u.team === "fusao" ? "Fusao" : "Infraestrutura",
          total: userTasks.length,
          completed: userCompleted,
          inProgress: userTasks.filter((t) => t.status === "em_andamento").length,
          pending: userTasks.filter((t) => t.status === "pendente").length,
          rate: userTasks.length > 0 ? Math.round((userCompleted / userTasks.length) * 100) : 0,
        }
      })
      .sort((a, b) => b.completed - a.completed)

    // Status distribution for pie chart
    const statusDistribution = [
      { name: "Pendente", value: pending, fill: "var(--chart-4)" },
      { name: "Em andamento", value: inProgress, fill: "var(--chart-1)" },
      { name: "Concluida", value: completed, fill: "var(--chart-2)" },
    ].filter((s) => s.value > 0)

    // Recent tasks (last 10)
    const { data: recentTasks } = await supabase
      .from("task_assignments")
      .select("id, title, status, priority, created_at, assigned_to_user:users!assigned_to(full_name)")
      .eq("company_id", companyId)
      .order("created_at", { ascending: false })
      .limit(10)

    return NextResponse.json({
      stats: {
        total,
        pending,
        inProgress,
        completed,
        unassigned,
        urgent,
        high,
        activeUsers: allUsers.filter((u) => u.active && u.role === "user").length,
      },
      teamStats,
      userPerformance,
      statusDistribution,
      recentTasks: recentTasks || [],
    })
  } catch (err) {
    console.error("Dashboard stats error:", err)
    return NextResponse.json({ error: "Erro ao carregar dados" }, { status: 500 })
  }
}
