"use client"

import { ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { LogOut, Phone } from "lucide-react"

interface DashboardLayoutProps {
  children: ReactNode
  title: string
  role: string
  onLogout: () => void
}

export default function DashboardLayout({ children, title, role, onLogout }: DashboardLayoutProps) {
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
          <Button variant="outline" size="sm" onClick={onLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Выход
          </Button>
        </div>
      </header>
      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
