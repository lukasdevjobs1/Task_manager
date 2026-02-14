import { NextResponse } from "next/server"
import { getSession } from "@/lib/auth"
import { createAdminClient } from "@/lib/supabase/server"

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ count: 0 })
  }

  try {
    const supabase = await createAdminClient()
    const { count } = await supabase
      .from("notifications")
      .select("id", { count: "exact", head: true })
      .eq("user_id", session.id)
      .eq("read", false)

    return NextResponse.json({ count: count || 0 })
  } catch {
    return NextResponse.json({ count: 0 })
  }
}
