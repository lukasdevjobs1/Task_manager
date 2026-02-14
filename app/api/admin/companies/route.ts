import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"
import bcryptjs from "bcryptjs"

export async function GET() {
  const session = await getSession()
  if (!session || !session.is_super_admin) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()

  try {
    const { data: companies, error } = await supabase
      .from("companies")
      .select("*")
      .order("name")

    if (error) throw error

    // Get stats for each company
    const companiesWithStats = await Promise.all(
      (companies || []).map(async (company) => {
        const { count: userCount } = await supabase
          .from("users")
          .select("id", { count: "exact", head: true })
          .eq("company_id", company.id)

        const { count: taskCount } = await supabase
          .from("task_assignments")
          .select("id", { count: "exact", head: true })
          .eq("company_id", company.id)

        const { count: completedCount } = await supabase
          .from("task_assignments")
          .select("id", { count: "exact", head: true })
          .eq("company_id", company.id)
          .eq("status", "concluida")

        return {
          ...company,
          userCount: userCount || 0,
          taskCount: taskCount || 0,
          completedCount: completedCount || 0,
        }
      })
    )

    return NextResponse.json({ companies: companiesWithStats })
  } catch (err) {
    console.error("Companies error:", err)
    return NextResponse.json({ error: "Erro ao carregar empresas" }, { status: 500 })
  }
}

export async function POST(request: Request) {
  const session = await getSession()
  if (!session || !session.is_super_admin) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const supabase = await createAdminClient()

  try {
    const { name, slug, admin_username, admin_password, admin_full_name } = await request.json()

    if (!name || !slug) {
      return NextResponse.json({ error: "Nome e slug sao obrigatorios" }, { status: 400 })
    }

    // Check if slug exists
    const { data: existing } = await supabase
      .from("companies")
      .select("id")
      .eq("slug", slug.toLowerCase())
      .limit(1)

    if (existing && existing.length > 0) {
      return NextResponse.json({ error: "Slug ja existe" }, { status: 400 })
    }

    // Create company
    const { data: company, error: companyError } = await supabase
      .from("companies")
      .insert({
        name,
        slug: slug.toLowerCase(),
        active: true,
        created_at: new Date().toISOString(),
      })
      .select()
      .single()

    if (companyError) throw companyError

    // Create admin user for the company if provided
    if (admin_username && admin_password && admin_full_name) {
      const hash = await bcryptjs.hash(admin_password, 10)
      await supabase.from("users").insert({
        company_id: company.id,
        username: admin_username,
        password_hash: hash,
        full_name: admin_full_name,
        team: "fusao",
        role: "admin",
        active: true,
        created_at: new Date().toISOString(),
      })
    }

    return NextResponse.json({ company })
  } catch (err) {
    console.error("Create company error:", err)
    return NextResponse.json({ error: "Erro ao criar empresa" }, { status: 500 })
  }
}
