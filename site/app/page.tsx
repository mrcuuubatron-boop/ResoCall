"use client"

import { useEffect, useState } from "react"
import { AuthPanel } from "@/components/auth-panel"
import { UserPanel } from "@/components/user-panel"
import { EngineerPanel } from "@/components/engineer-panel"
import { AdminPanel } from "@/components/admin-panel"

type Role = "admin" | "engineer" | "user"

interface SavedSession {
  login: string
  password: string
  role: Role
  token: string
}

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userRole, setUserRole] = useState<Role | "">("")
  const [credentials, setCredentials] = useState<SavedSession | null>(null)

  const handleLogin = (session: SavedSession) => {
    setUserRole(session.role)
    setCredentials(session)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    clearSession()
    setIsLoggedIn(false)
    setUserRole("")
    setCredentials(null)
  }

  // Если не авторизован - показываем страницу авторизации
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-zinc-900 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <header className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">ResoCall</h1>
            <p className="text-zinc-400">Анализ деятельности операторов call-центра с помощью ИИ</p>
          </header>
          <section className="bg-zinc-500 rounded-lg p-8">
            <AuthPanel onLogin={handleLogin} />
          </section>
        </div>
      </div>
    )
  }

  // Если авторизован - показываем панель соответствующую роли на всю страницу
  return (
    <>
      {userRole === "user" && credentials && <UserPanel onLogout={handleLogout} />}
      {userRole === "engineer" && credentials && <EngineerPanel onLogout={handleLogout} />}
      {userRole === "admin" && credentials && <AdminPanel onLogout={handleLogout} />}
    </>
  )
}
