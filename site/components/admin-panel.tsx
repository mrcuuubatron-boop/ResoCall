"use client"

import { useState, useEffect, useCallback } from "react"
import DashboardLayout from "./dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Play, Pause, RotateCcw, Square, Activity, Clock, CheckCircle, XCircle, AlertTriangle, Settings } from "lucide-react"

interface LogEntry {
  id: string
  timestamp: string
  level: "info" | "warning" | "error" | "success"
  message: string
}

interface RunError {
  id: string
  audioPath: string
  errorType: string
  message: string
}

interface RunHistory {
  id: string
  startTime: string
  endTime: string
  status: "completed" | "failed" | "stopped"
  processed: number
  errors: number
  errorList: RunError[]
}

interface ErrorStatItem {
  type: string
  count: number
  percentage: number
  audioFiles: { id: string; path: string; timestamp: string }[]
}

interface AdminPanelProps {
  onLogout: () => void
}

export function AdminPanel({ onLogout }: AdminPanelProps) {
  const [networkStatus, setNetworkStatus] = useState({ isRunning: false, isPaused: false })
  const [currentLogs, setCurrentLogs] = useState<LogEntry[]>([])
  const [runHistory, setRunHistory] = useState<RunHistory[]>([])
  const [errorStats, setErrorStats] = useState<ErrorStatItem[]>([])
  const [loading, setLoading] = useState(true)
  const [offline, setOffline] = useState(false)

  const [selectedRunErrors, setSelectedRunErrors] = useState<RunHistory | null>(null)
  const [selectedErrorType, setSelectedErrorType] = useState<ErrorStatItem | null>(null)
  const [showSettings, setShowSettings] = useState(false)

  // Первоначальная загрузка
  useEffect(() => {
    async function initialLoad() {
      try {
        const [statusRes, historyRes, errorsRes] = await Promise.all([
          fetch("/api/neural-network/status"),
          fetch("/api/neural-network/history"),
          fetch("/api/neural-network/errors-stats"),
        ])
        if (statusRes.ok) {
          const status = await statusRes.json()
          setNetworkStatus({ isRunning: status.isRunning, isPaused: status.isPaused })
        }
        if (historyRes.ok) setRunHistory(await historyRes.json())
        if (errorsRes.ok) setErrorStats(await errorsRes.json())
      } catch {
        setOffline(true)
      } finally {
        setLoading(false)
      }
    }
    initialLoad()
    fetchLogs()
  }, [])

  // Периодическая подгрузка логов (каждые 3 секунды)
  useEffect(() => {
    const interval = setInterval(fetchLogs, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchLogs = useCallback(async () => {
    try {
      const res = await fetch("/api/neural-network/logs")
      if (res.ok) {
        setCurrentLogs(await res.json())
        setOffline(false)
      }
    } catch {
      // ничего не делаем
    }
  }, [])

  const sendCommand = async (command: string) => {
    if (offline) {
      alert("Нет подключения к серверу")
      return
    }
    try {
      const res = await fetch(`/api/neural-network/${command}`, { method: "POST" })
      if (!res.ok) throw new Error("Команда не выполнена")
      // обновить статус
      const statusRes = await fetch("/api/neural-network/status")
      if (statusRes.ok) {
        const s = await statusRes.json()
        setNetworkStatus({ isRunning: s.isRunning, isPaused: s.isPaused })
      }
    } catch (err) {
      alert("Ошибка: " + (err instanceof Error ? err.message : "неизвестно"))
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case "success": return "text-green-600"
      case "warning": return "text-amber-600"
      case "error": return "text-red-600"
      default: return "text-neutral-600"
    }
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case "success": return <CheckCircle className="w-4 h-4" />
      case "warning": return <AlertTriangle className="w-4 h-4" />
      case "error": return <XCircle className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed": return <Badge className="bg-green-100 text-green-800 border-green-200">Завершен</Badge>
      case "failed": return <Badge className="bg-red-100 text-red-800 border-red-200">Ошибка</Badge>
      case "stopped": return <Badge className="bg-amber-100 text-amber-800 border-amber-200">Остановлен</Badge>
      default: return <Badge variant="outline">Неизвестно</Badge>
    }
  }

  return (
    <DashboardLayout title="Управление нейросетью" role="Администратор" onLogout={onLogout}>
      <div className="space-y-6">
        {offline && (
          <Card className="border-amber-200 bg-amber-50">
            <CardContent className="py-3 flex items-center gap-2 text-amber-800">
              <AlertTriangle className="w-5 h-5" />
              <span>Сервер недоступен. Управление невозможно, данные не обновляются.</span>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Статус нейросети</CardTitle>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  networkStatus.isRunning && !networkStatus.isPaused ? 'bg-green-500 animate-pulse' :
                  networkStatus.isPaused ? 'bg-amber-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm font-medium">
                  {networkStatus.isRunning && !networkStatus.isPaused ? 'Работает' :
                   networkStatus.isPaused ? 'Приостановлена' : 'Остановлена'}
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => sendCommand('start')} disabled={networkStatus.isRunning && !networkStatus.isPaused || offline} size="sm">
                <Play className="w-4 h-4 mr-2" /> Запуск
              </Button>
              <Button onClick={() => sendCommand('pause')} disabled={!networkStatus.isRunning || networkStatus.isPaused || offline} variant="outline" size="sm">
                <Pause className="w-4 h-4 mr-2" /> Пауза
              </Button>
              <Button onClick={() => sendCommand('stop')} disabled={!networkStatus.isRunning || offline} variant="outline" size="sm">
                <Square className="w-4 h-4 mr-2" /> Стоп
              </Button>
              <Button onClick={() => sendCommand('restart')} disabled={offline} variant="outline" size="sm">
                <RotateCcw className="w-4 h-4 mr-2" /> Перезапуск
              </Button>
              <Button onClick={() => setShowSettings(true)} variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" /> Настройки
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Статистика текущего запуска (заглушка) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Обработано</p>
                  <p className="text-2xl font-semibold mt-1">—</p>
                </div>
                <CheckCircle className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Ошибок</p>
                  <p className="text-2xl font-semibold mt-1">—</p>
                </div>
                <XCircle className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Время работы</p>
                  <p className="text-2xl font-semibold mt-1">—</p>
                </div>
                <Clock className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
        </div>

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
                  {currentLogs.length === 0 ? (
                    <div className="text-center py-8 text-neutral-500">Логи пока отсутствуют</div>
                  ) : (
                    currentLogs.map(log => (
                      <div key={log.id} className="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg">
                        <span className={`mt-0.5 ${getLevelColor(log.level)}`}>{getLevelIcon(log.level)}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-neutral-500 font-mono">{log.timestamp}</span>
                            <Badge variant="outline" className={`text-xs ${getLevelColor(log.level)}`}>{log.level.toUpperCase()}</Badge>
                          </div>
                          <p className="text-sm mt-1">{log.message}</p>
                        </div>
                      </div>
                    ))
                  )}
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
                  {runHistory.length === 0 ? (
                    <div className="text-center py-8 text-neutral-500">История пуста</div>
                  ) : (
                    runHistory.map(run => (
                      <div key={run.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Activity className="w-4 h-4 text-neutral-500" />
                            <span className="text-sm text-neutral-500">Запуск #{run.id}</span>
                          </div>
                          {getStatusBadge(run.status)}
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div><p className="text-neutral-500">Начало</p><p className="font-medium">{run.startTime}</p></div>
                          <div><p className="text-neutral-500">Окончание</p><p className="font-medium">{run.endTime}</p></div>
                          <div><p className="text-neutral-500">Обработано</p><p className="font-medium">{run.processed} звонков</p></div>
                          <div>
                            <p className="text-neutral-500">Ошибок</p>
                            <button className="font-medium text-red-600 hover:underline" onClick={() => setSelectedRunErrors(run)}>
                              {run.errors}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
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
                  {errorStats.length === 0 ? (
                    <div className="text-center py-8 text-green-600">Ошибок не зафиксировано</div>
                  ) : (
                    <>
                      {errorStats.map(stat => (
                        <div key={stat.type} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <button className="text-sm font-medium text-blue-600 hover:underline" onClick={() => setSelectedErrorType(stat)}>
                              {stat.type}
                            </button>
                            <div className="flex items-center gap-2">
                              <span className="text-sm text-neutral-500">{stat.count} случаев</span>
                              <Badge variant="outline">{stat.percentage}%</Badge>
                            </div>
                          </div>
                          <div className="w-full bg-neutral-100 rounded-full h-2">
                            <div className="bg-red-500 h-2 rounded-full" style={{ width: `${stat.percentage}%` }}></div>
                          </div>
                        </div>
                      ))}
                      <div className="pt-4 border-t">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Всего ошибок</span>
                          <span className="text-2xl font-semibold">{errorStats.reduce((s, st) => s + st.count, 0)}</span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Модальные окна без изменений, только данные из стейтов */}
      <Dialog open={!!selectedRunErrors} onOpenChange={() => setSelectedRunErrors(null)}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader><DialogTitle>Ошибки запуска #{selectedRunErrors?.id}</DialogTitle></DialogHeader>
          {selectedRunErrors && (
            <div className="flex-1 flex flex-col min-h-0">
              <div className="mb-4 p-4 bg-neutral-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div><span className="text-neutral-500">Время запуска:</span><span className="ml-2 font-medium">{selectedRunErrors.startTime}</span></div>
                  <div><span className="text-neutral-500">Всего ошибок:</span><span className="ml-2 font-medium text-red-600">{selectedRunErrors.errors}</span></div>
                </div>
              </div>
              <ScrollArea className="flex-1">
                <div className="space-y-3 pr-4">
                  {selectedRunErrors.errorList.map(error => (
                    <div key={error.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline" className="text-red-600 border-red-200">{error.errorType}</Badge>
                      </div>
                      <p className="text-sm text-neutral-600 mb-2">{error.message}</p>
                      <div className="flex items-center gap-2 p-2 bg-neutral-100 rounded text-sm">
                        <span className="text-neutral-500">Аудио:</span>
                        <code className="text-blue-600">{error.audioPath}</code>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={!!selectedErrorType} onOpenChange={() => setSelectedErrorType(null)}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader><DialogTitle>Ошибки: {selectedErrorType?.type}</DialogTitle></DialogHeader>
          {selectedErrorType && (
            <div className="flex-1 flex flex-col min-h-0">
              <div className="mb-4 p-4 bg-neutral-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Всего случаев:</span>
                  <span className="font-medium text-red-600">{selectedErrorType.count}</span>
                </div>
              </div>
              <ScrollArea className="flex-1">
                <div className="space-y-2 pr-4">
                  {selectedErrorType.audioFiles.map(file => (
                    <div key={file.id} className="border rounded-lg p-3 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                        <code className="text-sm text-blue-600">{file.path}</code>
                      </div>
                      <span className="text-xs text-neutral-500">{file.timestamp}</span>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader><DialogTitle>Настройки нейросети</DialogTitle></DialogHeader>
          <div className="flex-1 flex flex-col">
            <div className="p-8 text-center text-neutral-500">
              <Settings className="w-16 h-16 mx-auto mb-4 text-neutral-300" />
              <p className="text-lg font-medium mb-2">Настройки будут доступны позже</p>
              <p className="text-sm">Функционал настроек будет реализован совместно с командой бэкенда.</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
