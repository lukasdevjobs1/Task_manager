import { NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()
  const searchParams = request.nextUrl.searchParams
  const status = searchParams.get("status")
  const assignedTo = searchParams.get("assigned_to")
  const unassigned = searchParams.get("unassigned")

  try {
    let query = supabase
      .from("task_assignments")
      .select(
        "*, assigned_to_user:users!task_assignments_assigned_to_fkey(full_name, team), assigned_by_user:users!task_assignments_assigned_by_fkey(full_name)"
      )
      .eq("company_id", session.company_id)

    if (status) query = query.eq("status", status)
    if (assignedTo) query = query.eq("assigned_to", parseInt(assignedTo))
    if (unassigned === "true") query = query.is("assigned_to", null)

    const { data, error } = await query.order("created_at", { ascending: false })

    if (error) throw error

    return NextResponse.json({ tasks: data || [] })
  } catch (err) {
    console.error("Tasks fetch error:", err)
    return NextResponse.json({ error: "Erro ao carregar tarefas" }, { status: 500 })
  }
}

export async function POST(request: Request) {
  const session = await getSession()
  if (!session || session.role !== "admin") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()

  try {
    const body = await request.json()
    const { title, description, address, latitude, longitude, priority, due_date, assigned_to } = body

    if (!title?.trim()) {
      return NextResponse.json({ error: "Titulo e obrigatorio" }, { status: 400 })
    }

    const taskData: Record<string, unknown> = {
      company_id: session.company_id,
      assigned_by: session.id,
      title: title.trim(),
      description: description?.trim() || null,
      address: address?.trim() || null,
      latitude: latitude || null,
      longitude: longitude || null,
      status: "pendente",
      priority: priority || "media",
      due_date: due_date || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    if (assigned_to) {
      taskData.assigned_to = parseInt(assigned_to)
    }

    const { data, error } = await supabase
      .from("task_assignments")
      .insert(taskData)
      .select()
      .single()

    if (error) throw error

    // Create notification if assigned
    if (assigned_to) {
      await supabase.from("notifications").insert({
        user_id: parseInt(assigned_to),
        company_id: session.company_id,
        type: "task_assigned",
        title: "Nova tarefa atribuida",
        message: `A tarefa "${title}" foi atribuida a voce por ${session.full_name}.`,
        reference_id: data.id,
        read: false,
        created_at: new Date().toISOString(),
      })
    }

    return NextResponse.json({ task: data })
  } catch (err) {
    console.error("Task create error:", err)
    return NextResponse.json({ error: "Erro ao criar tarefa" }, { status: 500 })
  }
}
