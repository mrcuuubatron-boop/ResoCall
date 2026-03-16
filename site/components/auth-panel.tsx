"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface AuthPanelProps {
  onLogin: (role: string) => void
}

export function AuthPanel({ onLogin }: AuthPanelProps) {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    // Проверка логина и пароля
    if (login === "admin" && password === "admin") {
      onLogin("admin")
    } else if (login === "engineer" && password === "engineer") {
      onLogin("engineer")
    } else if (login === "user" && password === "user") {
      onLogin("user")
    } else {
      setError("Неверный логин или пароль")
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[300px]">
      <div className="bg-zinc-700 p-8 rounded-lg w-full max-w-md">
        <h2 className="text-white text-xl font-medium text-center mb-6">Авторизация</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              type="text"
              placeholder="Логин"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              className="bg-zinc-600 border-zinc-500 text-white placeholder:text-zinc-400"
            />
          </div>
          <div>
            <Input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-zinc-600 border-zinc-500 text-white placeholder:text-zinc-400"
            />
          </div>
          {error && (
            <p className="text-red-400 text-sm text-center">{error}</p>
          )}
          <Button 
            type="submit" 
            className="w-full bg-zinc-600 hover:bg-zinc-500 text-white"
          >
            Войти
          </Button>
        </form>
        <div className="text-zinc-400 text-xs mt-4 text-center space-y-1">
          <p>Учетные данные для демо:</p>
          <p>admin / admin | engineer / engineer | user / user</p>
        </div>
      </div>
    </div>
  )
}
