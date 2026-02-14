import { NextResponse } from "next/server"
import { createAdminClient } from "@/lib/supabase/server"
import { createSession } from "@/lib/auth"
import bcryptjs from "bcryptjs"

export async function POST(request: Request) {
  try {
    const { username, password } = await request.json()

    if (!username || !password) {
      return NextResponse.json(
        { error: "Username e senha sao obrigatorios" },
        { status: 400 }
      )
    }

    const supabase = await createAdminClient()

    // Fetch user with company data
    const { data: users, error } = await supabase
      .from("users")
      .select("id, company_id, username, password_hash, full_name, team, role, is_super_admin, active, companies(name, active)")
      .eq("username", username)
      .limit(1)

    if (error || !users || users.length === 0) {
      return NextResponse.json(
        { error: "Usuario ou senha incorretos" },
        { status: 401 }
      )
    }

    const user = users[0]
    const company = user.companies as { name: string; active: boolean } | null

    // Check if user and company are active
    if (!user.active) {
      return NextResponse.json(
        { error: "Sua conta esta desativada. Contate o administrador." },
        { status: 403 }
      )
    }

    if (company && !company.active) {
      return NextResponse.json(
        { error: "Sua empresa esta desativada. Contate o suporte." },
        { status: 403 }
      )
    }

    // Verify bcrypt password
    const isValid = await bcryptjs.compare(password, user.password_hash)
    if (!isValid) {
      return NextResponse.json(
        { error: "Usuario ou senha incorretos" },
        { status: 401 }
      )
    }

    // Create session
    const sessionUser = {
      id: user.id,
      company_id: user.company_id,
      company_name: company?.name || "Sem empresa",
      username: user.username,
      full_name: user.full_name,
      team: user.team,
      role: user.role,
      is_super_admin: user.is_super_admin || false,
    }

    await createSession(sessionUser)

    return NextResponse.json({ success: true, user: sessionUser })
  } catch (err) {
    console.error("Login error:", err)
    return NextResponse.json(
      { error: "Erro interno do servidor" },
      { status: 500 }
    )
  }
}
