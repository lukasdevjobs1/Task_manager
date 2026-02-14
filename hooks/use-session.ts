"use client"

import useSWR from "swr"
import type { SessionUser } from "@/lib/auth"

const fetcher = (url: string) =>
  fetch(url).then((r) => {
    if (!r.ok) throw new Error("Not authenticated")
    return r.json()
  })

export function useSession() {
  const { data, error, isLoading, mutate } = useSWR<{ user: SessionUser }>(
    "/api/auth/session",
    fetcher,
    {
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    }
  )

  return {
    user: data?.user ?? null,
    isLoading,
    isError: !!error,
    mutate,
  }
}
