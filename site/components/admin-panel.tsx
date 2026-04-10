"use client"

import { useState } from "react"
import DashboardLayout from "./dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
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
  { 
    id: "1", 
    startTime: "2026-03-20 10:00:00", 
    endTime: "2026-03-20 14:30:15", 
    status: "completed", 
    processed: 342, 
    errors: 3,
    errorList: [
      { id: "e1", audioPath: "/audio/2026-03-20/call_8235.mp3", errorType: "ASR Timeout", message: "Превышено время ожидания транскрипции" },
      { id: "e2", audioPath: "/audio/2026-03-20/call_8267.mp3", errorType: "Low Audio Quality", message: "Низкое качество аудио, невозможно распознать речь" },
      { id: "e3", audioPath: "/audio/2026-03-20/call_8301.mp3", errorType: "Processing Error", message: "Ошибка обработки данных" },
    ]
  },
  { 
    id: "2", 
    startTime: "2026-03-19 09:00:00", 
    endTime: "2026-03-19 15:22:43", 
    status: "completed", 
    processed: 398, 
    errors: 5,
    errorList: [
      { id: "e4", audioPath: "/audio/2026-03-19/call_7892.mp3", errorType: "ASR Timeout", message: "Превышено время ожидания" },
      { id: "e5", audioPath: "/audio/2026-03-19/call_7901.mp3", errorType: "Network Error", message: "Ошибка сети" },
      { id: "e6", audioPath: "/audio/2026-03-19/call_7945.mp3", errorType: "Low Audio Quality", message: "Низкое качество записи" },
      { id: "e7", audioPath: "/audio/2026-03-19/call_7980.mp3", errorType: "Low Audio Quality", message: "Шум на записи" },
      { id: "e8", audioPath: "/audio/2026-03-19/call_8012.mp3", errorType: "Processing Error", message: "Внутренняя ошибка" },
    ]
  },
  { 
    id: "3", 
    startTime: "2026-03-18 08:30:00", 
    endTime: "2026-03-18 12:15:00", 
    status: "stopped", 
    processed: 156, 
    errors: 2,
    errorList: [
      { id: "e9", audioPath: "/audio/2026-03-18/call_7501.mp3", errorType: "ASR Timeout", message: "Timeout" },
      { id: "e10", audioPath: "/audio/2026-03-18/call_7534.mp3", errorType: "Network Error", message: "Потеря соединения" },
    ]
  },
  { 
    id: "4", 
    startTime: "2026-03-17 10:00:00", 
    endTime: "2026-03-17 14:45:21", 
    status: "completed", 
    processed: 421, 
    errors: 7,
    errorList: [
      { id: "e11", audioPath: "/audio/2026-03-17/call_7102.mp3", errorType: "ASR Timeout", message: "Timeout exceeded" },
      { id: "e12", audioPath: "/audio/2026-03-17/call_7156.mp3", errorType: "Low Audio Quality", message: "Плохое качество" },
      { id: "e13", audioPath: "/audio/2026-03-17/call_7189.mp3", errorType: "Low Audio Quality", message: "Помехи" },
      { id: "e14", audioPath: "/audio/2026-03-17/call_7234.mp3", errorType: "Network Error", message: "Ошибка сети" },
      { id: "e15", audioPath: "/audio/2026-03-17/call_7267.mp3", errorType: "Processing Error", message: "Ошибка парсинга" },
      { id: "e16", audioPath: "/audio/2026-03-17/call_7301.mp3", errorType: "Processing Error", message: "Ошибка модели" },
      { id: "e17", audioPath: "/audio/2026-03-17/call_7345.mp3", errorType: "ASR Timeout", message: "Timeout" },
    ]
  },
  { 
    id: "5", 
    startTime: "2026-03-16 09:15:00", 
    endTime: "2026-03-16 11:30:00", 
    status: "failed", 
    processed: 89, 
    errors: 45,
    errorList: Array.from({ length: 45 }, (_, i) => ({
      id: `e${18 + i}`,
      audioPath: `/audio/2026-03-16/call_${6500 + i}.mp3`,
      errorType: ["ASR Timeout", "Low Audio Quality", "Network Error", "Processing Error"][i % 4],
      message: "Массовый сбой системы"
    }))
  },
]

const errorStats: ErrorStatItem[] = [
  { 
    type: "ASR Timeout", 
    count: 12, 
    percentage: 25,
    audioFiles: [
      { id: "1", path: "/audio/2026-03-20/call_8235.mp3", timestamp: "2026-03-20 10:15:23" },
      { id: "2", path: "/audio/2026-03-19/call_7892.mp3", timestamp: "2026-03-19 09:45:12" },
      { id: "3", path: "/audio/2026-03-18/call_7501.mp3", timestamp: "2026-03-18 08:52:34" },
      { id: "4", path: "/audio/2026-03-17/call_7102.mp3", timestamp: "2026-03-17 10:23:45" },
      { id: "5", path: "/audio/2026-03-17/call_7345.mp3", timestamp: "2026-03-17 14:12:33" },
      { id: "6", path: "/audio/2026-03-16/call_6500.mp3", timestamp: "2026-03-16 09:20:11" },
      { id: "7", path: "/audio/2026-03-16/call_6504.mp3", timestamp: "2026-03-16 09:35:22" },
      { id: "8", path: "/audio/2026-03-16/call_6508.mp3", timestamp: "2026-03-16 09:48:55" },
      { id: "9", path: "/audio/2026-03-16/call_6512.mp3", timestamp: "2026-03-16 10:01:43" },
      { id: "10", path: "/audio/2026-03-16/call_6516.mp3", timestamp: "2026-03-16 10:15:32" },
      { id: "11", path: "/audio/2026-03-16/call_6520.mp3", timestamp: "2026-03-16 10:28:21" },
      { id: "12", path: "/audio/2026-03-16/call_6524.mp3", timestamp: "2026-03-16 10:41:10" },
    ]
  },
  { 
    type: "Low Audio Quality", 
    count: 18, 
    percentage: 37,
    audioFiles: Array.from({ length: 18 }, (_, i) => ({
      id: String(i + 1),
      path: `/audio/low_quality/call_${7000 + i * 10}.mp3`,
      timestamp: `2026-03-${15 + (i % 5)} ${9 + (i % 8)}:${String((i * 7) % 60).padStart(2, '0')}:00`
    }))
  },
  { 
    type: "Network Error", 
    count: 8, 
    percentage: 17,
    audioFiles: Array.from({ length: 8 }, (_, i) => ({
      id: String(i + 1),
      path: `/audio/network_error/call_${8000 + i * 15}.mp3`,
      timestamp: `2026-03-${16 + (i % 4)} ${10 + (i % 6)}:${String((i * 11) % 60).padStart(2, '0')}:00`
    }))
  },
  { 
    type: "Processing Error", 
    count: 10, 
    percentage: 21,
    audioFiles: Array.from({ length: 10 }, (_, i) => ({
      id: String(i + 1),
      path: `/audio/processing_error/call_${9000 + i * 12}.mp3`,
      timestamp: `2026-03-${17 + (i % 3)} ${11 + (i % 5)}:${String((i * 9) % 60).padStart(2, '0')}:00`
    }))
  },
]

interface AdminPanelProps {
  onLogout: () => void
}

export function AdminPanel({ onLogout }: AdminPanelProps) {
  const [isRunning, setIsRunning] = useState(true)
  const [isPaused, setIsPaused] = useState(false)
  
  // Модальные окна
  const [selectedRunErrors, setSelectedRunErrors] = useState<RunHistory | null>(null)
  const [selectedErrorType, setSelectedErrorType] = useState<ErrorStatItem | null>(null)
  const [showSettings, setShowSettings] = useState(false)

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
              <Button 
                onClick={() => setShowSettings(true)}
                variant="outline"
                size="sm"
              >
                <Settings className="w-4 h-4 mr-2" />
                Настройки
              </Button>
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
                          <button 
                            className="font-medium text-red-600 hover:underline cursor-pointer"
                            onClick={() => setSelectedRunErrors(run)}
                          >
                            {run.errors}
                          </button>
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
                        <button 
                          className="text-sm font-medium text-blue-600 hover:underline cursor-pointer"
                          onClick={() => setSelectedErrorType(stat)}
                        >
                          {stat.type}
                        </button>
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

      {/* Модальное окно: Ошибки запуска */}
      <Dialog open={!!selectedRunErrors} onOpenChange={() => setSelectedRunErrors(null)}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Ошибки запуска #{selectedRunErrors?.id}</DialogTitle>
          </DialogHeader>
          {selectedRunErrors && (
            <div className="flex-1 flex flex-col min-h-0">
              <div className="mb-4 p-4 bg-neutral-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-neutral-500">Время запуска:</span>
                    <span className="ml-2 font-medium">{selectedRunErrors.startTime}</span>
                  </div>
                  <div>
                    <span className="text-neutral-500">Всего ошибок:</span>
                    <span className="ml-2 font-medium text-red-600">{selectedRunErrors.errors}</span>
                  </div>
                </div>
              </div>
              <ScrollArea className="flex-1">
                <div className="space-y-3 pr-4">
                  {selectedRunErrors.errorList.map((error) => (
                    <div key={error.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline" className="text-red-600 border-red-200">
                          {error.errorType}
                        </Badge>
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

      {/* Модальное окно: Ошибки по типу */}
      <Dialog open={!!selectedErrorType} onOpenChange={() => setSelectedErrorType(null)}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Ошибки: {selectedErrorType?.type}</DialogTitle>
          </DialogHeader>
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
                  {selectedErrorType.audioFiles.map((file) => (
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

      {/* Модальное окно: Настройки */}
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Настройки нейросети</DialogTitle>
          </DialogHeader>
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
