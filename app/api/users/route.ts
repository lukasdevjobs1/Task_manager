import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()

  try {
    const { data, error } = await supabase
      .from("users")
      .select("id, full_name, team, role, active")
      .eq("company_id", session.company_id)
      .eq("active", true)
      .order("full_name")

    if (error) throw error

    return NextResponse.json({ users: data || [] })
  } catch (err) {
    console.error("Users fetch error:", err)
    return NextResponse.json({ error: "Erro ao carregar usuarios" }, { status: 500 })
  }
}
