"use client"

import { useState } from "react"
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
    setIsLoggedIn(false)
    setUserRole("")
    setCredentials(null)
  }

  // Если не авторизован - показываем страницу авторизации
  if (!isLoggedIn) {
    return <AuthPanel onLogin={handleLogin} />
  }

  // Если авторизован - показываем панель соответствующую роли
  return (
    <>
      {userRole === "user" && credentials && <UserPanel onLogout={handleLogout} />}
      {userRole === "engineer" && credentials && <EngineerPanel onLogout={handleLogout} />}
      {userRole === "admin" && credentials && <AdminPanel onLogout={handleLogout} />}
    </>
  )
}
