import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getSession()
  if (!session || !session.is_super_admin) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const { id } = await params
  const supabase = await createAdminClient()

  try {
    const body = await request.json()

    if (body.action === "toggle_status") {
      const { data: company } = await supabase
        .from("companies")
        .select("active")
        .eq("id", parseInt(id))
        .single()

      if (!company) {
        return NextResponse.json({ error: "Empresa nao encontrada" }, { status: 404 })
      }

      await supabase
        .from("companies")
        .update({ active: !company.active })
        .eq("id", parseInt(id))

      return NextResponse.json({ success: true })
    }

    if (body.name) {
      await supabase
        .from("companies")
        .update({ name: body.name })
        .eq("id", parseInt(id))
      return NextResponse.json({ success: true })
    }

    return NextResponse.json({ error: "Acao invalida" }, { status: 400 })
  } catch (err) {
    console.error("Company update error:", err)
    return NextResponse.json({ error: "Erro ao atualizar empresa" }, { status: 500 })
  }
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getSession()
  if (!session || !session.is_super_admin) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const { id } = await params
  const supabase = await createAdminClient()
  const companyId = parseInt(id)

  try {
    // Cascade delete
    await supabase.from("notifications").delete().eq("company_id", companyId)
    await supabase.from("assignment_photos").delete().in(
      "assignment_id",
      (await supabase.from("task_assignments").select("id").eq("company_id", companyId)).data?.map((t) => t.id) || []
    )
    await supabase.from("task_assignments").delete().eq("company_id", companyId)
    await supabase.from("users").delete().eq("company_id", companyId)
    await supabase.from("companies").delete().eq("id", companyId)

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error("Delete company error:", err)
    return NextResponse.json({ error: "Erro ao excluir empresa" }, { status: 500 })
  }
}
