import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const { id } = await params
  const supabase = await createAdminClient()

  try {
    const { data, error } = await supabase
      .from("task_assignments")
      .select(
        "*, assigned_to_user:users!task_assignments_assigned_to_fkey(full_name, team), assigned_by_user:users!task_assignments_assigned_by_fkey(full_name)"
      )
      .eq("id", parseInt(id))
      .eq("company_id", session.company_id)
      .single()

    if (error || !data) {
      return NextResponse.json({ error: "Tarefa nao encontrada" }, { status: 404 })
    }

    // Get photos
    const { data: photos } = await supabase
      .from("assignment_photos")
      .select("*")
      .eq("assignment_id", parseInt(id))
      .order("uploaded_at", { ascending: false })

    return NextResponse.json({ task: data, photos: photos || [] })
  } catch (err) {
    console.error("Task detail error:", err)
    return NextResponse.json({ error: "Erro ao carregar tarefa" }, { status: 500 })
  }
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getSession()
  if (!session || session.role !== "admin") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const { id } = await params
  const supabase = await createAdminClient()

  try {
    const body = await request.json()
    const updateData: Record<string, unknown> = {
      updated_at: new Date().toISOString(),
    }

    if (body.status) updateData.status = body.status
    if (body.title) updateData.title = body.title
    if (body.description !== undefined) updateData.description = body.description
    if (body.priority) updateData.priority = body.priority
    if (body.address !== undefined) updateData.address = body.address
    if (body.assigned_to !== undefined) updateData.assigned_to = body.assigned_to

    const { data, error } = await supabase
      .from("task_assignments")
      .update(updateData)
      .eq("id", parseInt(id))
      .eq("company_id", session.company_id)
      .select()
      .single()

    if (error) throw error

    // Notify if reassigned
    if (body.assigned_to && body.assigned_to !== data.assigned_to) {
      await supabase.from("notifications").insert({
        user_id: body.assigned_to,
        company_id: session.company_id,
        type: "task_assigned",
        title: "Tarefa atribuida a voce",
        message: `A tarefa "${data.title}" foi atribuida a voce.`,
        reference_id: data.id,
        read: false,
        created_at: new Date().toISOString(),
      })
    }

    return NextResponse.json({ task: data })
  } catch (err) {
    console.error("Task update error:", err)
    return NextResponse.json({ error: "Erro ao atualizar tarefa" }, { status: 500 })
  }
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getSession()
  if (!session || session.role !== "admin") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const { id } = await params
  const supabase = await createAdminClient()

  try {
    // Delete photos first
    await supabase.from("assignment_photos").delete().eq("assignment_id", parseInt(id))

    // Delete notifications
    await supabase.from("notifications").delete().eq("reference_id", parseInt(id))

    // Delete task
    const { error } = await supabase
      .from("task_assignments")
      .delete()
      .eq("id", parseInt(id))
      .eq("company_id", session.company_id)

    if (error) throw error

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error("Task delete error:", err)
    return NextResponse.json({ error: "Erro ao excluir tarefa" }, { status: 500 })
  }
}
