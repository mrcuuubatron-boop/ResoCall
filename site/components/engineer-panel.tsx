"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import DashboardLayout from "./dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Users, 
  MessageSquare, 
  CheckCircle, 
  AlertCircle, 
  CalendarIcon,
  X,
  Play,
  ArrowLeft,
  ArrowUpDown
} from "lucide-react"
import { format, subDays, startOfDay, endOfDay } from "date-fns"
import { ru } from "date-fns/locale"
import { DateRange } from "react-day-picker"

// ---------- Типы ----------
export interface Message {
  speaker: 'operator' | 'client'
  text: string
  timestamp?: string
}

export type Sentiment = 'positive' | 'neutral' | 'negative'

export interface Call {
  id: string
  employeeId: string
  clientId: string
  date: string
  duration: number
  transcript: Message[]
  sentiment: Sentiment
  scriptCompliance: number
  category: string
  isProcessed: boolean
  errorReason?: string
  audioUrl: string
}

export interface Employee {
  id: string
  name: string
  position: string
}

export interface Client {
  id: string
  name: string
}

// ---------- Утилиты ----------
function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function formatDate(dateStr: string): string {
  try {
    return format(new Date(dateStr), "dd.MM.yyyy HH:mm", { locale: ru })
  } catch {
    return dateStr
  }
}

function getSentimentLabel(s: Sentiment): string {
  switch (s) {
    case 'positive': return 'Позитивный'
    case 'neutral': return 'Нейтральный'
    case 'negative': return 'Негативный'
    default: return s
  }
}

function getSentimentColor(s: Sentiment): string {
  switch (s) {
    case 'positive': return 'bg-green-100 text-green-800'
    case 'neutral': return 'bg-neutral-100 text-neutral-800'
    case 'negative': return 'bg-red-100 text-red-800'
    default: return ''
  }
}

function calculateEmployeeRating(
  empId: string,
  calls: Call[]
): { avgScriptCompliance: number; avgSentiment: number; rating: number; callsCount: number } {
  const empCalls = calls.filter(c => c.employeeId === empId && c.isProcessed)
  if (empCalls.length === 0) return { avgScriptCompliance: 0, avgSentiment: 0, rating: 0, callsCount: 0 }
  
  const avgScript = Math.round(empCalls.reduce((s, c) => s + c.scriptCompliance, 0) / empCalls.length)
  const sentimentMap = { positive: 5, neutral: 3, negative: 1 }
  const totalSent = empCalls.reduce((s, c) => s + (sentimentMap[c.sentiment] || 0), 0)
  const avgSent = Math.round((totalSent / empCalls.length) * 20)
  const rating = Math.round(avgScript * 0.6 + avgSent * 0.4)
  return { avgScriptCompliance: avgScript, avgSentiment: avgSent, rating, callsCount: empCalls.length }
}

// ---------- Компонент EngineerPanel ----------
interface EngineerPanelProps {
  onLogout: () => void
}

export function EngineerPanel({ onLogout }: EngineerPanelProps) {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [calls, setCalls] = useState<Call[]>([])
  const [unprocessedCalls, setUnprocessedCalls] = useState<Call[]>([])
  const [loadingCalls, setLoadingCalls] = useState(false)
  const [loadingEmployees, setLoadingEmployees] = useState(false)

  // Флаги состояния подключения
  const [dataSource, setDataSource] = useState<'online' | 'offline'>('offline')

  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subDays(new Date(), 7),
    to: new Date()
  })
  const [dialogFilterDateRange, setDialogFilterDateRange] = useState<DateRange | undefined>()
  const [dialogFilterScript, setDialogFilterScript] = useState("all")
  const [dialogFilterSentiment, setDialogFilterSentiment] = useState("all")
  const [selectedCall, setSelectedCall] = useState<Call | null>(null)
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null)
  const [unprocessedCallError, setUnprocessedCallError] = useState<Call | null>(null)
  const [ratingSortAsc, setRatingSortAsc] = useState(false)

  // Загрузка справочников (сотрудники и клиенты) – не блокирует интерфейс
  useEffect(() => {
    async function loadDictionaries() {
      setLoadingEmployees(true)
      try {
        const [empRes, clientRes] = await Promise.all([
          fetch("/api/employees"),
          fetch("/api/clients")
        ])
        if (!empRes.ok || !clientRes.ok) throw new Error("Ошибка справочников")
        const emps = await empRes.json()
        const cls = await clientRes.json()
        setEmployees(emps)
        setClients(cls)
        setDataSource('online')
      } catch {
        setEmployees([])
        setClients([])
      } finally {
        setLoadingEmployees(false)
      }
    }
    loadDictionaries()

    // Необработанные звонки
    fetch("/api/calls/unprocessed")
      .then(res => res.json())
      .then(data => setUnprocessedCalls(data))
      .catch(() => setUnprocessedCalls([]))
  }, [])

  // Загрузка звонков по периоду
  useEffect(() => {
    if (!dateRange?.from) return
    async function fetchCalls() {
      setLoadingCalls(true)
      try {
        const from = startOfDay(dateRange.from!).toISOString()
        const to = endOfDay(dateRange.to || dateRange.from!).toISOString()
        const res = await fetch(`/api/calls?from=${from}&to=${to}`)
        if (!res.ok) throw new Error("Ошибка звонков")
        const data = await res.json()
        setCalls(data)
      } catch {
        setCalls([])
      } finally {
        setLoadingCalls(false)
      }
    }
    fetchCalls()
  }, [dateRange])

  const getEmployeeById = useCallback((id: string) => employees.find(e => e.id === id) || null, [employees])
  const getClientById = useCallback((id: string) => clients.find(c => c.id === id) || null, [clients])

  const filteredCalls = useMemo(() => calls.filter(c => c.isProcessed), [calls])

  const sentimentStats = useMemo(() => {
    const stats = { positive: 0, neutral: 0, negative: 0 }
    filteredCalls.forEach(c => stats[c.sentiment]++)
    return stats
  }, [filteredCalls])

  const totalCalls = filteredCalls.length
  const avgScriptCompliance = useMemo(() => {
    if (totalCalls === 0) return 0
    return Math.round(filteredCalls.reduce((acc, c) => acc + c.scriptCompliance, 0) / totalCalls)
  }, [filteredCalls, totalCalls])

  const employeeRatings = useMemo(() => {
    const ratings = employees.map(emp => ({
      ...emp,
      ...calculateEmployeeRating(emp.id, calls)
    }))
    return ratingSortAsc 
      ? ratings.sort((a, b) => a.rating - b.rating)
      : ratings.sort((a, b) => b.rating - a.rating)
  }, [employees, calls, ratingSortAsc])

  const dialogsFiltered = useMemo(() => {
    let result = filteredCalls
    if (dialogFilterDateRange?.from) {
      const start = startOfDay(dialogFilterDateRange.from)
      const end = dialogFilterDateRange.to ? endOfDay(dialogFilterDateRange.to) : endOfDay(dialogFilterDateRange.from)
      result = result.filter(c => {
        const d = new Date(c.date)
        return d >= start && d <= end
      })
    }
    if (dialogFilterScript !== "all") {
      if (dialogFilterScript === "gt90") result = result.filter(c => c.scriptCompliance > 90)
      if (dialogFilterScript === "gt70") result = result.filter(c => c.scriptCompliance > 70)
      if (dialogFilterScript === "lt70") result = result.filter(c => c.scriptCompliance < 70)
      if (dialogFilterScript === "lt50") result = result.filter(c => c.scriptCompliance < 50)
    }
    if (dialogFilterSentiment !== "all") {
      result = result.filter(c => c.sentiment === dialogFilterSentiment)
    }
    return result
  }, [filteredCalls, dialogFilterDateRange, dialogFilterScript, dialogFilterSentiment])

  const selectedEmployeeCalls = useMemo(() => {
    if (!selectedEmployeeId) return []
    return filteredCalls.filter(c => c.employeeId === selectedEmployeeId)
  }, [filteredCalls, selectedEmployeeId])

  const selectedEmployee = selectedEmployeeId ? getEmployeeById(selectedEmployeeId) : null

  // Если выбран сотрудник – показываем его диалоги
  if (selectedEmployeeId && selectedEmployee) {
    return (
      <DashboardLayout title="Диалоги сотрудника" role="Аналитик" onLogout={onLogout}>
        <div className="space-y-6">
          <Button variant="outline" onClick={() => setSelectedEmployeeId(null)}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Назад
          </Button>
          <Card>
            <CardHeader>
              <CardTitle>{selectedEmployee.name}</CardTitle>
              <p className="text-sm text-neutral-500">{selectedEmployee.position}</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                  <p className="text-2xl font-bold">{selectedEmployeeCalls.length}</p>
                  <p className="text-sm text-neutral-500">Всего звонков</p>
                </div>
                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                  <p className="text-2xl font-bold">
                    {selectedEmployeeCalls.length
                      ? Math.round(selectedEmployeeCalls.reduce((a, c) => a + c.scriptCompliance, 0) / selectedEmployeeCalls.length)
                      : 0}%
                  </p>
                  <p className="text-sm text-neutral-500">Соблюдение скрипта</p>
                </div>
                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                  <p className="text-2xl font-bold">
                    {calculateEmployeeRating(selectedEmployeeId, calls).rating}
                  </p>
                  <p className="text-sm text-neutral-500">Рейтинг</p>
                </div>
              </div>
              <div className="space-y-3">
                {selectedEmployeeCalls.map(call => {
                  const client = getClientById(call.clientId)
                  return (
                    <div key={call.id} className="border rounded-lg p-4 hover:bg-neutral-50 cursor-pointer transition-colors"
                      onClick={() => setSelectedCall(call)}>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-blue-600 hover:underline">
                            Диалог #{call.id.replace('call-', '')}
                          </p>
                          <p className="text-sm text-neutral-500">
                            {client?.name} | {formatDate(call.date)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={getSentimentColor(call.sentiment)}>{getSentimentLabel(call.sentiment)}</Badge>
                          <Badge variant="outline">{formatDuration(call.duration)}</Badge>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
        <CallDetailModal call={selectedCall} onClose={() => setSelectedCall(null)}
          onEmployeeClick={(empId) => { setSelectedCall(null); setSelectedEmployeeId(empId); }}
          employees={employees} clients={clients} />
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Аналитика и статистика" role="Аналитик" onLogout={onLogout}>
      <div className="space-y-6">
        {/* Предупреждение о недоступности данных */}
        {dataSource === 'offline' && !loadingEmployees && (
          <Card className="border-amber-200 bg-amber-50">
            <CardContent className="py-3 flex items-center gap-2 text-amber-800">
              <AlertCircle className="w-5 h-5" />
              <span>Нет подключения к серверу. Данные могут быть неактуальны.</span>
            </CardContent>
          </Card>
        )}

        {/* Выбор периода */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4 flex-wrap">
              <span className="text-sm text-neutral-500">Период:</span>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="min-w-[280px] justify-start text-left">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateRange?.from ? (
                      dateRange.to ? (
                        <>
                          {format(dateRange.from, "dd.MM.yyyy", { locale: ru })} -{" "}
                          {format(dateRange.to, "dd.MM.yyyy", { locale: ru })}
                        </>
                      ) : (
                        format(dateRange.from, "dd.MM.yyyy", { locale: ru })
                      )
                    ) : (
                      "Выберите период"
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={dateRange?.from}
                    selected={dateRange}
                    onSelect={setDateRange}
                    numberOfMonths={2}
                    locale={ru}
                  />
                </PopoverContent>
              </Popover>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => setDateRange({ from: new Date(), to: new Date() })}>
                  Сегодня
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setDateRange({ from: subDays(new Date(), 7), to: new Date() })}>
                  Неделя
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setDateRange({ from: subDays(new Date(), 30), to: new Date() })}>
                  Месяц
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Всего звонков</p>
                  <p className="text-2xl font-semibold mt-1">{totalCalls}</p>
                </div>
                <MessageSquare className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Соблюдение скрипта</p>
                  <p className="text-2xl font-semibold mt-1">{avgScriptCompliance}%</p>
                </div>
                <CheckCircle className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Сотрудников</p>
                  <p className="text-2xl font-semibold mt-1">{employees.length}</p>
                </div>
                <Users className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Необработано</p>
                  <p className="text-2xl font-semibold mt-1">{unprocessedCalls.length}</p>
                </div>
                <AlertCircle className="w-10 h-10 text-amber-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Тональность */}
        <Card>
          <CardHeader>
            <CardTitle>Анализ тональности</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(['positive', 'neutral', 'negative'] as Sentiment[]).map(sent => (
                <div key={sent} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{getSentimentLabel(sent)}</span>
                    <span className="font-medium">
                      {sentimentStats[sent]} ({totalCalls > 0 ? Math.round(sentimentStats[sent] / totalCalls * 100) : 0}%)
                    </span>
                  </div>
                  <div className="w-full bg-neutral-100 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${sent === 'positive' ? 'bg-green-500' : sent === 'neutral' ? 'bg-neutral-400' : 'bg-red-500'}`}
                      style={{ width: `${totalCalls > 0 ? (sentimentStats[sent] / totalCalls) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              ))}
              {totalCalls === 0 && (
                <div className="text-sm text-neutral-500 text-center">Нет данных для анализа</div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Табы */}
        <Tabs defaultValue="dialogs" className="space-y-4">
          <TabsList>
            <TabsTrigger value="dialogs">Статистика диалогов</TabsTrigger>
            <TabsTrigger value="employees">Рейтинг сотрудников</TabsTrigger>
            <TabsTrigger value="unprocessed">Необработанные звонки</TabsTrigger>
          </TabsList>

          <TabsContent value="dialogs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Все диалоги</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4 mb-6 pb-6 border-b">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-neutral-500">Дата:</span>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" size="sm">
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {dialogFilterDateRange?.from ? (
                            dialogFilterDateRange.to ? (
                              `${format(dialogFilterDateRange.from, "dd.MM", { locale: ru })} - ${format(dialogFilterDateRange.to, "dd.MM", { locale: ru })}`
                            ) : (
                              format(dialogFilterDateRange.from, "dd.MM.yyyy", { locale: ru })
                            )
                          ) : "Все даты"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar initialFocus mode="range" selected={dialogFilterDateRange} onSelect={setDialogFilterDateRange} numberOfMonths={2} locale={ru} />
                      </PopoverContent>
                    </Popover>
                    {dialogFilterDateRange && (
                      <Button variant="ghost" size="sm" onClick={() => setDialogFilterDateRange(undefined)}>
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-neutral-500">Скрипт:</span>
                    <Select value={dialogFilterScript} onValueChange={setDialogFilterScript}>
                      <SelectTrigger className="w-[160px]"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Все</SelectItem>
                        <SelectItem value="gt90">Больше 90%</SelectItem>
                        <SelectItem value="gt70">Больше 70%</SelectItem>
                        <SelectItem value="lt70">Меньше 70%</SelectItem>
                        <SelectItem value="lt50">Меньше 50%</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-neutral-500">Настроение:</span>
                    <Select value={dialogFilterSentiment} onValueChange={setDialogFilterSentiment}>
                      <SelectTrigger className="w-[160px]"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Все</SelectItem>
                        <SelectItem value="positive">Позитивный</SelectItem>
                        <SelectItem value="neutral">Нейтральный</SelectItem>
                        <SelectItem value="negative">Негативный</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <p className="text-sm text-neutral-500 mb-4">Найдено: {dialogsFiltered.length} диалогов</p>
                <ScrollArea className="h-[500px]">
                  <div className="space-y-3">
                    {dialogsFiltered.length === 0 ? (
                      <div className="text-center py-8 text-neutral-500">Нет диалогов, удовлетворяющих фильтрам</div>
                    ) : (
                      dialogsFiltered.map(call => {
                        const emp = getEmployeeById(call.employeeId)
                        const client = getClientById(call.clientId)
                        return (
                          <div key={call.id} className="border rounded-lg p-4 hover:bg-neutral-50 transition-colors">
                            <div className="flex items-center justify-between mb-2">
                              <button className="font-medium text-blue-600 hover:underline text-left" onClick={() => setSelectedCall(call)}>
                                Диалог #{call.id.replace('call-', '')}
                              </button>
                              <div className="flex items-center gap-2">
                                <Badge className={getSentimentColor(call.sentiment)}>{getSentimentLabel(call.sentiment)}</Badge>
                                <Badge variant="outline">{call.scriptCompliance}%</Badge>
                              </div>
                            </div>
                            <div className="text-sm text-neutral-500">
                              <span>Сотрудник: </span>
                              <button className="text-blue-600 hover:underline" onClick={() => setSelectedEmployeeId(call.employeeId)}>
                                {emp?.name ?? "Неизвестно"}
                              </button>
                              <span> | Клиент: {client?.name ?? "Неизвестно"}</span>
                            </div>
                            <div className="text-sm text-neutral-400 mt-1">
                              {formatDate(call.date)} | {formatDuration(call.duration)} | {call.category}
                            </div>
                          </div>
                        )
                      })
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="employees" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Сотрудники Call-центра</CardTitle>
                    <p className="text-sm text-neutral-500 mt-1">Рейтинг = 60% соблюдение скрипта + 40% средняя тональность</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setRatingSortAsc(!ratingSortAsc)}>
                    <ArrowUpDown className="w-4 h-4 mr-2" />
                    {ratingSortAsc ? "По возрастанию" : "По убыванию"}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {employeeRatings.length === 0 ? (
                    <div className="text-center py-8 text-neutral-500">Нет данных о сотрудниках</div>
                  ) : (
                    employeeRatings.map((emp, index) => (
                      <div key={emp.id} className="border rounded-lg p-4 hover:bg-neutral-50 transition-colors">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                              index === 0 ? 'bg-yellow-400 text-yellow-900' :
                              index === 1 ? 'bg-neutral-300 text-neutral-700' :
                              index === 2 ? 'bg-amber-600 text-white' : 'bg-neutral-900 text-white'
                            }`}>
                              {index + 1}
                            </div>
                            <div>
                              <button className="font-medium text-blue-600 hover:underline text-left" onClick={() => setSelectedEmployeeId(emp.id)}>
                                {emp.name}
                              </button>
                              <p className="text-sm text-neutral-500">{emp.callsCount} звонков</p>
                            </div>
                          </div>
                          <Badge variant="outline" className="text-lg px-3 py-1">{emp.rating}</Badge>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-neutral-500">Соблюдение скрипта</span>
                              <span className="font-medium">{emp.avgScriptCompliance}%</span>
                            </div>
                            <Progress value={emp.avgScriptCompliance} className="h-2" />
                          </div>
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-neutral-500">Средняя тональность</span>
                              <span className="font-medium">{emp.avgSentiment}%</span>
                            </div>
                            <Progress value={emp.avgSentiment} className="h-2" />
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="unprocessed">
            <Card>
              <CardHeader>
                <CardTitle>Необработанные нейросетью звонки</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {unprocessedCalls.length === 0 ? (
                    <div className="text-center py-8 text-green-600">Все звонки обработаны</div>
                  ) : (
                    unprocessedCalls.map(call => {
                      const client = getClientById(call.clientId)
                      const emp = getEmployeeById(call.employeeId)
                      return (
                        <div key={call.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{client?.name ?? "Неизвестно"}</p>
                              <p className="text-sm text-neutral-500">
                                Сотрудник: {emp?.name ?? "Неизвестно"} | {formatDate(call.date)}
                              </p>
                              <button className="text-sm text-red-600 hover:underline mt-1" onClick={() => setUnprocessedCallError(call)}>
                                {call.errorReason}
                              </button>
                            </div>
                            <Badge variant="outline">{formatDuration(call.duration)}</Badge>
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <CallDetailModal call={selectedCall} onClose={() => setSelectedCall(null)}
        onEmployeeClick={(empId) => { setSelectedCall(null); setSelectedEmployeeId(empId); }}
        employees={employees} clients={clients} />
      
      <Dialog open={!!unprocessedCallError} onOpenChange={() => setUnprocessedCallError(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Ошибка обработки звонка</DialogTitle></DialogHeader>
          {unprocessedCallError && (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-neutral-500">Причина ошибки:</p>
                <p className="font-medium text-red-600">{unprocessedCallError.errorReason}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-500">Дата звонка:</p>
                <p>{formatDate(unprocessedCallError.date)}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-500">Длительность:</p>
                <p>{formatDuration(unprocessedCallError.duration)}</p>
              </div>
              <div className="flex items-center gap-2">
                <Play className="w-4 h-4" />
                <a href={unprocessedCallError.audioUrl} className="text-blue-600 hover:underline">{unprocessedCallError.audioUrl}</a>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}

// ---------- Модальное окно диалога ----------
function CallDetailModal({ 
  call, onClose, onEmployeeClick, employees, clients 
}: { 
  call: Call | null
  onClose: () => void
  onEmployeeClick: (employeeId: string) => void
  employees: Employee[]
  clients: Client[]
}) {
  if (!call) return null
  const employee = employees.find(e => e.id === call.employeeId) || null
  const client = clients.find(c => c.id === call.clientId) || null

  return (
    <Dialog open={!!call} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Диалог #{call.id.replace('call-', '')}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="text-sm text-neutral-500">Сотрудник:</p>
              <button className="font-medium text-blue-600 hover:underline" onClick={() => onEmployeeClick(call.employeeId)}>
                {employee?.name ?? "Неизвестно"}
              </button>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Клиент:</p>
              <p className="font-medium">{client?.name ?? "Неизвестно"}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Дата:</p>
              <p>{formatDate(call.date)}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Длительность:</p>
              <p>{formatDuration(call.duration)}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Настроение:</p>
              <Badge className={getSentimentColor(call.sentiment)}>{getSentimentLabel(call.sentiment)}</Badge>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Соблюдение скрипта:</p>
              <p className="font-medium">{call.scriptCompliance}%</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-3 border rounded-lg">
            <Play className="w-5 h-5 text-neutral-500" />
            <a href={call.audioUrl} className="text-blue-600 hover:underline">{call.audioUrl}</a>
          </div>
          <div>
            <p className="text-sm text-neutral-500 mb-2">Текст диалога:</p>
            <ScrollArea className="h-[300px] border rounded-lg p-4">
              <div className="space-y-3">
                {call.transcript.map((msg, i) => (
                  <div key={i} className={`p-3 rounded-lg ${msg.speaker === 'operator' ? 'bg-blue-50 ml-0 mr-8' : 'bg-neutral-100 ml-8 mr-0'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-medium text-neutral-500">{msg.speaker === 'operator' ? 'Оператор' : 'Клиент'}</span>
                      {msg.timestamp && <span className="text-xs text-neutral-400">{msg.timestamp}</span>}
                    </div>
                    <p className="text-sm">{msg.text}</p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
