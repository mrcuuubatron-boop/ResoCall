"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Phone, ServerCrash, ShieldCheck } from "lucide-react"
import { fetchBackendHealth, loginWithBackend, type BackendHealthResponse, type LoginResponse } from "@/lib/backend-api"

interface AuthPanelProps {
  onLogin: (session: {
    login: string
    password: string
    role: "admin" | "engineer" | "user"
    token: string
  }) => void
}

export function AuthPanel({ onLogin }: AuthPanelProps) {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [backendHealth, setBackendHealth] = useState<BackendHealthResponse | null>(null)
  const [backendError, setBackendError] = useState<string>("")
  const [isCheckingBackend, setIsCheckingBackend] = useState(true)

  useEffect(() => {
    let active = true

    const checkBackend = async () => {
      try {
        const health = await fetchBackendHealth()
        if (active) {
          setBackendHealth(health)
          setBackendError("")
        }
      } catch (checkError) {
        if (active) {
          setBackendHealth(null)
          setBackendError(checkError instanceof Error ? checkError.message : "Backend недоступен")
        }
      } finally {
        if (active) {
          setIsCheckingBackend(false)
        }
      }
    }

    void checkBackend()

    return () => {
      active = false
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    try {
      const response = await loginWithBackend(login, password)
      if (!response.ok) {
        setError("Сервер вернул некорректный ответ авторизации")
        return
      }

      onLogin({
        login,
        password,
        role: response.role,
        token: response.token,
      })
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось выполнить вход")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <Card className="w-full max-w-md mx-4 shadow-lg">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-neutral-900 rounded-2xl flex items-center justify-center">
              <Phone className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl">Call-центр Аналитика</CardTitle>
          <CardDescription>
            Система анализа звонков операторов
          </CardDescription>
          <div className="flex items-center justify-center gap-2 pt-2">
            {isCheckingBackend ? (
              <Badge variant="secondary">Проверка backend...</Badge>
            ) : backendHealth ? (
              <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                <ShieldCheck className="mr-1 h-3.5 w-3.5" />
                Backend: {backendHealth.status}
              </Badge>
            ) : (
              <Badge variant="destructive">
                <ServerCrash className="mr-1 h-3.5 w-3.5" />
                {backendError || "Backend недоступен"}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="login">Логин</Label>
              <Input
                id="login"
                type="text"
                placeholder="Введите логин"
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            <Button type="submit" className="w-full">
              Войти
            </Button>

            <div className="text-xs text-neutral-500 text-center space-y-1 pt-2">
              <p>Тестовые данные backend:</p>
              <p className="font-mono">user/user | engineer/engineer | admin/admin</p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
