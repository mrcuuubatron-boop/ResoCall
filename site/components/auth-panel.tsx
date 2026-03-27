"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Phone } from "lucide-react"

interface AuthPanelProps {
  onLogin: (role: string) => void
}

export function AuthPanel({ onLogin }: AuthPanelProps) {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState<string>("operator")
  const [error, setError] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    // Проверка учетных данных
    const validCredentials: Record<string, { password: string; role: string }> = {
      user: { password: "user", role: "operator" },
      analyst: { password: "analyst", role: "analyst" },
      admin: { password: "admin", role: "admin" },
    }

    const user = validCredentials[login]
    
    if (user && user.password === password) {
      onLogin(user.role)
    } else {
      setError("Неверный логин или пароль")
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

            <div className="space-y-2">
              <Label htmlFor="role">Роль</Label>
              <Select value={role} onValueChange={setRole}>
                <SelectTrigger id="role">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="operator">Сотрудник Call-центра</SelectItem>
                  <SelectItem value="analyst">Аналитик</SelectItem>
                  <SelectItem value="admin">Администратор</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            <Button type="submit" className="w-full">
              Войти
            </Button>

            <div className="text-xs text-neutral-500 text-center space-y-1 pt-2">
              <p>Тестовые данные:</p>
              <p className="font-mono">user/user | analyst/analyst | admin/admin</p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
