import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"
import bcryptjs from "bcryptjs"

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

    // Toggle status
    if (body.action === "toggle_status") {
      const { data: user } = await supabase
        .from("users")
        .select("active")
        .eq("id", parseInt(id))
        .eq("company_id", session.company_id)
        .single()

      if (!user) {
        return NextResponse.json({ error: "Usuario nao encontrado" }, { status: 404 })
      }

      await supabase
        .from("users")
        .update({ active: !user.active })
        .eq("id", parseInt(id))
        .eq("company_id", session.company_id)

      return NextResponse.json({ success: true })
    }

    // Change password
    if (body.action === "change_password") {
      if (!body.password || body.password.length < 6) {
        return NextResponse.json({ error: "Senha deve ter no minimo 6 caracteres" }, { status: 400 })
      }

      const hash = await bcryptjs.hash(body.password, 10)
      await supabase
        .from("users")
        .update({ password_hash: hash })
        .eq("id", parseInt(id))
        .eq("company_id", session.company_id)

      return NextResponse.json({ success: true })
    }

    return NextResponse.json({ error: "Acao invalida" }, { status: 400 })
  } catch (err) {
    console.error("User update error:", err)
    return NextResponse.json({ error: "Erro ao atualizar usuario" }, { status: 500 })
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
    // Delete user's notifications
    await supabase.from("notifications").delete().eq("user_id", parseInt(id))
    // Delete user's task assignments
    await supabase.from("task_assignments").delete().eq("assigned_to", parseInt(id))
    // Delete user
    await supabase.from("users").delete().eq("id", parseInt(id)).eq("company_id", session.company_id)

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error("Delete user error:", err)
    return NextResponse.json({ error: "Erro ao excluir usuario" }, { status: 500 })
  }
}
