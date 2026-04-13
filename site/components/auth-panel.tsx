"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface AuthPanelProps {
  onLogin: (login: string, password: string) => Promise<void>
}

export function AuthPanel({ onLogin }: AuthPanelProps) {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsSubmitting(true)

    try {
      await onLogin(login, password)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError("Неверный логин или пароль")
      }
    } finally {
      setIsSubmitting(false)
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
            disabled={isSubmitting}
            className="w-full bg-zinc-600 hover:bg-zinc-500 text-white"
          >
            {isSubmitting ? "Вход..." : "Войти"}
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
