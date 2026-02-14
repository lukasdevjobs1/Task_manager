import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"
import bcryptjs from "bcryptjs"

export async function GET() {
  const session = await getSession()
  if (!session || session.role !== "admin") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()

  try {
    const { data, error } = await supabase
      .from("users")
      .select("id, company_id, username, full_name, team, role, is_super_admin, active, created_at")
      .eq("company_id", session.company_id)
      .order("full_name")

    if (error) throw error

    return NextResponse.json({ users: data || [] })
  } catch (err) {
    console.error("Admin users error:", err)
    return NextResponse.json({ error: "Erro ao carregar usuarios" }, { status: 500 })
  }
}

export async function POST(request: Request) {
  const session = await getSession()
  if (!session || session.role !== "admin") {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()

  try {
    const { username, password, full_name, team, role } = await request.json()

    if (!username || !password || !full_name || !team) {
      return NextResponse.json({ error: "Todos os campos sao obrigatorios" }, { status: 400 })
    }

    if (password.length < 6) {
      return NextResponse.json({ error: "Senha deve ter no minimo 6 caracteres" }, { status: 400 })
    }

    // Check if username exists
    const { data: existing } = await supabase
      .from("users")
      .select("id")
      .eq("username", username)
      .limit(1)

    if (existing && existing.length > 0) {
      return NextResponse.json({ error: "Nome de usuario ja existe" }, { status: 400 })
    }

    const password_hash = await bcryptjs.hash(password, 10)

    const { data, error } = await supabase
      .from("users")
      .insert({
        company_id: session.company_id,
        username,
        password_hash,
        full_name,
        team,
        role: role || "user",
        active: true,
        created_at: new Date().toISOString(),
      })
      .select()
      .single()

    if (error) throw error

    return NextResponse.json({ user: data })
  } catch (err) {
    console.error("Create user error:", err)
    return NextResponse.json({ error: "Erro ao criar usuario" }, { status: 500 })
  }
}
