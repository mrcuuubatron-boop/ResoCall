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

interface AuthCredentials {
  login: string
  password: string
}

interface LoginResponse {
  ok: boolean
  role: Role
  token: string
}

const SESSION_STORAGE_KEY = "resocall_auth_session"

function isRole(value: string): value is Role {
  return value === "admin" || value === "engineer" || value === "user"
}

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
}

function saveSession(session: SavedSession): void {
  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
}

function loadSession(): SavedSession | null {
  const raw = window.localStorage.getItem(SESSION_STORAGE_KEY)
  if (!raw) {
    return null
  }

  try {
    const session = JSON.parse(raw) as SavedSession
    if (!isRole(session.role) || !session.login || !session.password || !session.token) {
      return null
    }
    return session
  } catch {
    return null
  }
}

function clearSession(): void {
  window.localStorage.removeItem(SESSION_STORAGE_KEY)
}

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userRole, setUserRole] = useState<Role | "">("")
  const [credentials, setCredentials] = useState<AuthCredentials | null>(null)

  useEffect(() => {
    const session = loadSession()
    if (!session) {
      clearSession()
      return
    }

    setUserRole(session.role)
    setCredentials({ login: session.login, password: session.password })
    setIsLoggedIn(true)
  }, [])

  const handleLogin = async (login: string, password: string) => {
    const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ login, password }),
    })

    if (!response.ok) {
      throw new Error("Неверный логин или пароль")
    }

    const data = (await response.json()) as LoginResponse
    if (!data.ok || !isRole(data.role) || !data.token) {
      throw new Error("Сервер вернул некорректный ответ авторизации")
    }

    const session: SavedSession = {
      login,
      password,
      role: data.role,
      token: data.token,
    }

    saveSession(session)

    setUserRole(data.role)
    setCredentials({ login, password })
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
    <div className="min-h-screen bg-zinc-900 flex flex-col">
      {userRole === "user" && credentials && (
        <UserPanel
          onLogout={handleLogout}
          login={credentials.login}
          password={credentials.password}
        />
      )}
      {userRole === "engineer" && credentials && (
        <EngineerPanel
          onLogout={handleLogout}
          login={credentials.login}
          password={credentials.password}
        />
      )}
      {userRole === "admin" && credentials && (
        <AdminPanel
          onLogout={handleLogout}
          login={credentials.login}
          password={credentials.password}
        />
      )}
    </div>
  )
}
