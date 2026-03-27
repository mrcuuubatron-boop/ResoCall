"use client"

import { useState } from "react"
import DashboardLayout from "./dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Play, Pause, RotateCcw, Square, Activity, Clock, CheckCircle, XCircle, AlertTriangle } from "lucide-react"

interface LogEntry {
  id: string
  timestamp: string
  level: "info" | "warning" | "error" | "success"
  message: string
}

interface RunHistory {
  id: string
  startTime: string
  endTime: string
  status: "completed" | "failed" | "stopped"
  processed: number
  errors: number
}

const currentLogs: LogEntry[] = [
  { id: "1", timestamp: "15:45:23", level: "info", message: "Начало обработки звонка #8234" },
  { id: "2", timestamp: "15:45:25", level: "success", message: "ASR: Транскрипция завершена для звонка #8234" },
  { id: "3", timestamp: "15:45:26", level: "success", message: "Sentiment Analysis: Определена тональность - позитивная (87%)" },
  { id: "4", timestamp: "15:45:27", level: "info", message: "Script Compliance: Проверка соблюдения скрипта" },
  { id: "5", timestamp: "15:45:28", level: "success", message: "Звонок #8234 успешно обработан" },
  { id: "6", timestamp: "15:45:30", level: "info", message: "Начало обработки звонка #8235" },
  { id: "7", timestamp: "15:45:32", level: "warning", message: "ASR: Низкое качество аудио для звонка #8235" },
  { id: "8", timestamp: "15:45:35", level: "error", message: "Ошибка обработки звонка #8235: Timeout exceeded" },
  { id: "9", timestamp: "15:45:40", level: "info", message: "Начало обработки звонка #8236" },
  { id: "10", timestamp: "15:45:42", level: "success", message: "ASR: Транскрипция завершена для звонка #8236" },
]

const runHistory: RunHistory[] = [
  { id: "1", startTime: "2026-03-20 10:00:00", endTime: "2026-03-20 14:30:15", status: "completed", processed: 342, errors: 3 },
  { id: "2", startTime: "2026-03-19 09:00:00", endTime: "2026-03-19 15:22:43", status: "completed", processed: 398, errors: 5 },
  { id: "3", startTime: "2026-03-18 08:30:00", endTime: "2026-03-18 12:15:00", status: "stopped", processed: 156, errors: 2 },
  { id: "4", startTime: "2026-03-17 10:00:00", endTime: "2026-03-17 14:45:21", status: "completed", processed: 421, errors: 7 },
  { id: "5", startTime: "2026-03-16 09:15:00", endTime: "2026-03-16 11:30:00", status: "failed", processed: 89, errors: 45 },
]

const errorStats = [
  { type: "ASR Timeout", count: 12, percentage: 25 },
  { type: "Low Audio Quality", count: 18, percentage: 37 },
  { type: "Network Error", count: 8, percentage: 17 },
  { type: "Processing Error", count: 10, percentage: 21 },
]

interface AdminPanelProps {
  onLogout: () => void
}

export function AdminPanel({ onLogout }: AdminPanelProps) {
  const [isRunning, setIsRunning] = useState(true)
  const [isPaused, setIsPaused] = useState(false)
  const [autoRestart, setAutoRestart] = useState(true)
  const [enableNotifications, setEnableNotifications] = useState(true)

  const handleStart = () => {
    setIsRunning(true)
    setIsPaused(false)
  }

  const handlePause = () => {
    setIsPaused(true)
  }

  const handleStop = () => {
    setIsRunning(false)
    setIsPaused(false)
  }

  const handleRestart = () => {
    setIsRunning(true)
    setIsPaused(false)
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case "success":
        return "text-green-600"
      case "warning":
        return "text-amber-600"
      case "error":
        return "text-red-600"
      default:
        return "text-neutral-600"
    }
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case "success":
        return <CheckCircle className="w-4 h-4" />
      case "warning":
        return <AlertTriangle className="w-4 h-4" />
      case "error":
        return <XCircle className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800 border-green-200">Завершен</Badge>
      case "failed":
        return <Badge className="bg-red-100 text-red-800 border-red-200">Ошибка</Badge>
      case "stopped":
        return <Badge className="bg-amber-100 text-amber-800 border-amber-200">Остановлен</Badge>
      default:
        return <Badge variant="outline">Неизвестно</Badge>
    }
  }

  return (
    <DashboardLayout title="Управление нейросетью" role="Администратор" onLogout={onLogout}>
      <div className="space-y-6">
        {/* Статус нейросети */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Статус нейросети</CardTitle>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isRunning && !isPaused ? 'bg-green-500 animate-pulse' : isPaused ? 'bg-amber-500' : 'bg-red-500'}`}></div>
                <span className="text-sm font-medium">
                  {isRunning && !isPaused ? 'Работает' : isPaused ? 'Приостановлена' : 'Остановлена'}
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button 
                onClick={handleStart} 
                disabled={isRunning && !isPaused}
                size="sm"
              >
                <Play className="w-4 h-4 mr-2" />
                Запуск
              </Button>
              <Button 
                onClick={handlePause} 
                disabled={!isRunning || isPaused}
                variant="outline"
                size="sm"
              >
                <Pause className="w-4 h-4 mr-2" />
                Пауза
              </Button>
              <Button 
                onClick={handleStop} 
                disabled={!isRunning}
                variant="outline"
                size="sm"
              >
                <Square className="w-4 h-4 mr-2" />
                Стоп
              </Button>
              <Button 
                onClick={handleRestart}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Перезапуск
              </Button>
            </div>

            <div className="border-t pt-4 space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="auto-restart" className="cursor-pointer">
                  Автоматический перезапуск при ошибках
                </Label>
                <Switch
                  id="auto-restart"
                  checked={autoRestart}
                  onCheckedChange={setAutoRestart}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="notifications" className="cursor-pointer">
                  Уведомления об ошибках
                </Label>
                <Switch
                  id="notifications"
                  checked={enableNotifications}
                  onCheckedChange={setEnableNotifications}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Статистика текущего запуска */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Обработано</p>
                  <p className="text-2xl font-semibold mt-1">342</p>
                </div>
                <CheckCircle className="w-10 h-10 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Ошибок</p>
                  <p className="text-2xl font-semibold mt-1">3</p>
                </div>
                <XCircle className="w-10 h-10 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Время работы</p>
                  <p className="text-2xl font-semibold mt-1">4ч 30м</p>
                </div>
                <Clock className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Табы */}
        <Tabs defaultValue="current" className="space-y-4">
          <TabsList>
            <TabsTrigger value="current">Текущие логи</TabsTrigger>
            <TabsTrigger value="history">История запусков</TabsTrigger>
            <TabsTrigger value="errors">Статистика ошибок</TabsTrigger>
          </TabsList>

          <TabsContent value="current">
            <Card>
              <CardHeader>
                <CardTitle>Логи текущего запуска</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {currentLogs.map((log) => (
                    <div key={log.id} className="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg">
                      <span className={`mt-0.5 ${getLevelColor(log.level)}`}>
                        {getLevelIcon(log.level)}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-neutral-500 font-mono">{log.timestamp}</span>
                          <Badge variant="outline" className={`text-xs ${getLevelColor(log.level)}`}>
                            {log.level.toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-sm mt-1">{log.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>История предыдущих запусков</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {runHistory.map((run) => (
                    <div key={run.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Activity className="w-4 h-4 text-neutral-500" />
                          <span className="text-sm text-neutral-500">Запуск #{run.id}</span>
                        </div>
                        {getStatusBadge(run.status)}
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-neutral-500">Начало</p>
                          <p className="font-medium">{run.startTime}</p>
                        </div>
                        <div>
                          <p className="text-neutral-500">Окончание</p>
                          <p className="font-medium">{run.endTime}</p>
                        </div>
                        <div>
                          <p className="text-neutral-500">Обработано</p>
                          <p className="font-medium">{run.processed} звонков</p>
                        </div>
                        <div>
                          <p className="text-neutral-500">Ошибок</p>
                          <p className="font-medium text-red-600">{run.errors}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="errors">
            <Card>
              <CardHeader>
                <CardTitle>Статистика ошибок за все запуски</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {errorStats.map((stat, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{stat.type}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-neutral-500">{stat.count} случаев</span>
                          <Badge variant="outline">{stat.percentage}%</Badge>
                        </div>
                      </div>
                      <div className="w-full bg-neutral-100 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full transition-all"
                          style={{ width: `${stat.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                  <div className="pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Всего ошибок</span>
                      <span className="text-2xl font-semibold">
                        {errorStats.reduce((acc, stat) => acc + stat.count, 0)}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
