"use client"

import { useState } from "react"
import { AuthPanel } from "@/components/auth-panel"
import { UserPanel } from "@/components/user-panel"
import { EngineerPanel } from "@/components/engineer-panel"
import { AdminPanel } from "@/components/admin-panel"

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userRole, setUserRole] = useState<string>("")

  const handleLogin = (role: string) => {
    setUserRole(role)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setUserRole("")
  }

  // Если не авторизован - показываем страницу авторизации
  if (!isLoggedIn) {
    return <AuthPanel onLogin={handleLogin} />
  }

  // Если авторизован - показываем панель соответствующую роли
  return (
    <>
      {userRole === "operator" && <UserPanel onLogout={handleLogout} />}
      {userRole === "analyst" && <EngineerPanel onLogout={handleLogout} />}
      {userRole === "admin" && <AdminPanel onLogout={handleLogout} />}
    </>
  )
}
