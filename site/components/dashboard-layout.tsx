"use client"

import { ReactNode, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { LogOut, Phone, ShieldCheck, ServerCrash } from "lucide-react"
import { fetchBackendHealth, type BackendHealthResponse } from "@/lib/backend-api"

interface DashboardLayoutProps {
  children: ReactNode
  title: string
  role: string
  onLogout: () => void
}

export default function DashboardLayout({ children, title, role, onLogout }: DashboardLayoutProps) {
  const [backendHealth, setBackendHealth] = useState<BackendHealthResponse | null>(null)
  const [backendError, setBackendError] = useState<string>("")

  useEffect(() => {
    let active = true

    const loadHealth = async () => {
      try {
        const health = await fetchBackendHealth()
        if (active) {
          setBackendHealth(health)
          setBackendError("")
        }
      } catch (error) {
        if (active) {
          setBackendHealth(null)
          setBackendError(error instanceof Error ? error.message : "Backend недоступен")
        }
      }
    }

    void loadHealth()

    return () => {
      active = false
    }
  }, [])

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white border-b border-neutral-200">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-neutral-900 rounded-lg flex items-center justify-center">
              <Phone className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-medium">{title}</h1>
              <p className="text-sm text-neutral-500">{role}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {backendHealth ? (
              <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                <ShieldCheck className="mr-1 h-3.5 w-3.5" />
                API {backendHealth.status} · DB {backendHealth.database_ok ? "ok" : "fail"}
              </Badge>
            ) : (
              <Badge variant="destructive">
                <ServerCrash className="mr-1 h-3.5 w-3.5" />
                {backendError || "API недоступен"}
              </Badge>
            )}
            <Button variant="outline" size="sm" onClick={onLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Выход
            </Button>
          </div>
        </div>
      </header>
      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
