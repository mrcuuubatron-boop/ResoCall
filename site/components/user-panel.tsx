"use client"

import { useState, useEffect, useMemo } from "react"
import DashboardLayout from "./dashboard-layout"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search, Clock, Calendar, Play, CalendarIcon } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { DateRange } from "react-day-picker"

interface Message {
  speaker: 'operator' | 'client'
  text: string
}

interface Call {
  id: string
  clientName: string
  date: string
  duration: number
  durationText?: string
  transcript: Message[]
  audioUrl: string
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainder = seconds % 60
  return `${minutes}:${remainder.toString().padStart(2, "0")}`
}

interface UserPanelProps {
  onLogout: () => void
}

export function UserPanel({ onLogout }: UserPanelProps) {
  const [serverCalls, setServerCalls] = useState<Call[]>([])
  const [loading, setLoading] = useState(true)
  const [dataSource, setDataSource] = useState<'server' | 'empty'>('server')

  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState<string>("duration")
  const [selectedCall, setSelectedCall] = useState<Call | null>(null)
  const [searchInDialog, setSearchInDialog] = useState("")
  const [dateRange, setDateRange] = useState<DateRange | undefined>()

  // Загрузка данных с сервера (тихо падаем при ошибке)
  useEffect(() => {
    async function fetchCalls() {
      try {
        const response = await fetch("/api/calls")
        if (!response.ok) throw new Error("Сервер вернул ошибку")
        const data: Call[] = await response.json()
        setServerCalls(data)
        setDataSource('server')
      } catch {
        // Сервер недоступен – остаёмся с пустым массивом
        setServerCalls([])
        setDataSource('empty')
      } finally {
        setLoading(false)
      }
    }
    fetchCalls()
  }, [])

  const filteredCalls = useMemo(() => {
    let result = serverCalls.filter(call => {
      const matchesSearch = call.clientName.toLowerCase().includes(searchQuery.toLowerCase())
      let matchesDate = true
      if (dateRange?.from) {
        const callDate = new Date(call.date)
        const startDate = new Date(dateRange.from)
        startDate.setHours(0, 0, 0, 0)
        const endDate = dateRange.to ? new Date(dateRange.to) : new Date(dateRange.from)
        endDate.setHours(23, 59, 59, 999)
        matchesDate = callDate >= startDate && callDate <= endDate
      }
      return matchesSearch && matchesDate
    })

    switch (sortBy) {
      case "date":
        result.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        break
      case "duration":
        result.sort((a, b) => b.duration - a.duration)
        break
      case "client":
        result.sort((a, b) => a.clientName.localeCompare(b.clientName))
        break
    }
    return result
  }, [serverCalls, searchQuery, dateRange, sortBy])

  const highlightText = (text: string, query: string) => {
    if (!query) return text
    const parts = text.split(new RegExp(`(${query})`, 'gi'))
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase()
        ? <mark key={i} className="bg-yellow-200">{part}</mark>
        : part
    )
  }

  return (
    <DashboardLayout title="Архив звонков" role="Сотрудник Call-центра" onLogout={onLogout}>
      <div className="space-y-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
                <Input
                  placeholder="Поиск по имени клиента..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full sm:w-auto min-w-[200px] justify-start text-left">
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
                      "Выберите дату"
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <CalendarComponent
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
              {dateRange && (
                <Button variant="ghost" size="sm" onClick={() => setDateRange(undefined)}>
                  Сбросить дату
                </Button>
              )}
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Сортировка" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="duration">По длительности</SelectItem>
                  <SelectItem value="client">По имени клиента</SelectItem>
                  <SelectItem value="date">По дате</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <Card>
            <CardContent className="py-12 text-center text-neutral-500">
              Загрузка звонков...
            </CardContent>
          </Card>
        ) : dataSource === 'empty' ? (
          <Card>
            <CardContent className="py-12 text-center text-neutral-500">
              Нет подключения к серверу. Данные звонков недоступны.
            </CardContent>
          </Card>
        ) : filteredCalls.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-neutral-500">
              Звонки не найдены
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {filteredCalls.map((call) => (
              <Card
                key={call.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedCall(call)}
              >
                <CardContent className="pt-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <h3 className="font-medium">{call.clientName}</h3>
                      <div className="flex flex-wrap gap-4 text-sm text-neutral-500">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {format(new Date(call.date), "dd.MM.yyyy HH:mm", { locale: ru })}
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {call.durationText || formatDuration(call.duration)}
                        </div>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Посмотреть
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Модальное окно с деталями звонка – без изменений */}
      <Dialog open={!!selectedCall} onOpenChange={() => setSelectedCall(null)}>
        <DialogContent className="w-[80vw] max-w-[80vw] h-[80vh] max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Детали звонка</DialogTitle>
          </DialogHeader>
          {selectedCall && (
            <div className="flex-1 flex flex-col space-y-4 overflow-hidden">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-neutral-500">Клиент</p>
                  <p className="font-medium">{selectedCall.clientName}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Дата и время</p>
                  <p className="font-medium">{format(new Date(selectedCall.date), "dd.MM.yyyy HH:mm", { locale: ru })}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Длительность</p>
                  <p className="font-medium">{selectedCall.durationText || formatDuration(selectedCall.duration)}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-neutral-500 mb-2">Аудиозапись</p>
                <div className="flex items-center gap-2 p-3 bg-neutral-100 rounded-lg">
                  <Play className="w-5 h-5 text-neutral-600" />
                  <span className="text-sm text-neutral-600">{selectedCall.audioUrl}</span>
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-neutral-500">Поиск в тексте</p>
                <Input
                  placeholder="Введите слово для поиска..."
                  value={searchInDialog}
                  onChange={(e) => setSearchInDialog(e.target.value)}
                />
              </div>
              <div className="flex-1 flex flex-col min-h-0">
                <p className="text-sm text-neutral-500 mb-2">Текст диалога:</p>
                <ScrollArea className="flex-1 border rounded-lg p-4">
                  <div className="space-y-3">
                    {selectedCall.transcript.map((message, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg ${
                          message.speaker === 'operator'
                            ? 'bg-blue-50 ml-0 mr-8'
                            : 'bg-neutral-100 ml-8 mr-0'
                        }`}
                      >
                        <p className="text-xs font-medium text-neutral-500 mb-1">
                          {message.speaker === 'operator' ? 'Оператор' : 'Клиент'}
                        </p>
                        <p className="text-sm">
                          {highlightText(message.text, searchInDialog)}
                        </p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
