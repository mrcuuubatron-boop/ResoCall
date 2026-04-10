"use client"

import { useState } from "react"
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
  duration: string
  transcript: Message[]
  audioUrl: string
}

const mockCalls: Call[] = [
  {
    id: "1",
    clientName: "Иванов Иван",
    date: "2026-03-20 10:30",
    duration: "5:23",
    transcript: [
      { speaker: 'operator', text: "Добрый день! Меня зовут Анна. Чем могу помочь?" },
      { speaker: 'client', text: "Здравствуйте! Хочу узнать о новых тарифах." },
      { speaker: 'operator', text: "С удовольствием расскажу! У нас есть несколько выгодных предложений..." },
      { speaker: 'client', text: "Отлично, расскажите подробнее." },
      { speaker: 'operator', text: "Конечно! Первый тариф включает безлимитные звонки..." },
    ],
    audioUrl: "/audio/call_001.mp3"
  },
  {
    id: "2",
    clientName: "Петрова Мария",
    date: "2026-03-20 09:15",
    duration: "8:45",
    transcript: [
      { speaker: 'operator', text: "Добрый день! Меня зовут Анна. Чем могу помочь?" },
      { speaker: 'client', text: "У меня проблема с оплатой, уже третий день не могу оплатить счет!" },
      { speaker: 'operator', text: "Понимаю ваше беспокойство. Давайте разберемся..." },
      { speaker: 'client', text: "Я уже звонил вчера, мне обещали перезвонить!" },
      { speaker: 'operator', text: "Приношу извинения за задержку. Сейчас проверю статус вашего обращения..." },
    ],
    audioUrl: "/audio/call_002.mp3"
  },
  {
    id: "3",
    clientName: "Сидоров Петр",
    date: "2026-03-19 16:20",
    duration: "3:12",
    transcript: [
      { speaker: 'operator', text: "Добрый день! Меня зовут Анна. Чем могу помочь?" },
      { speaker: 'client', text: "Добрый день, подскажите режим работы вашего офиса." },
      { speaker: 'operator', text: "Конечно! Наш офис работает с понедельника по пятницу с 9:00 до 18:00." },
      { speaker: 'client', text: "А в субботу?" },
      { speaker: 'operator', text: "В субботу мы работаем с 10:00 до 15:00." },
    ],
    audioUrl: "/audio/call_003.mp3"
  },
  {
    id: "4",
    clientName: "Ковалев Александр",
    date: "2026-03-19 14:05",
    duration: "12:30",
    transcript: [
      { speaker: 'operator', text: "Добрый день! Меня зовут Анна. Чем могу помочь?" },
      { speaker: 'client', text: "У меня серьезная техническая проблема, интернет не работает уже 2 дня!" },
      { speaker: 'operator', text: "Очень извиняюсь за неудобства. Давайте срочно разберемся..." },
      { speaker: 'client', text: "Я работаю из дома, мне срочно нужен интернет!" },
      { speaker: 'operator', text: "Понимаю критичность ситуации. Сейчас создам заявку с высоким приоритетом..." },
    ],
    audioUrl: "/audio/call_004.mp3"
  },
  {
    id: "5",
    clientName: "Новикова Елена",
    date: "2026-03-18 11:45",
    duration: "6:18",
    transcript: [
      { speaker: 'operator', text: "Добрый день! Меня зовут Анна. Чем могу помочь?" },
      { speaker: 'client', text: "Здравствуйте! Хочу поблагодарить вашу компанию за быстрое решение моей проблемы!" },
      { speaker: 'operator', text: "Спасибо за ваш отзыв! Мы рады, что смогли помочь." },
      { speaker: 'client', text: "Техник приехал вовремя и все починил за час." },
      { speaker: 'operator', text: "Передам благодарность нашей технической службе!" },
    ],
    audioUrl: "/audio/call_005.mp3"
  },
]

interface UserPanelProps {
  onLogout: () => void
}

export function UserPanel({ onLogout }: UserPanelProps) {
  const [calls, setCalls] = useState<Call[]>(mockCalls)
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState<string>("duration")
  const [selectedCall, setSelectedCall] = useState<Call | null>(null)
  const [searchInDialog, setSearchInDialog] = useState("")
  const [dateRange, setDateRange] = useState<DateRange | undefined>()

  const handleSort = (value: string) => {
    setSortBy(value)
    const sorted = [...calls].sort((a, b) => {
      switch (value) {
        case "date":
          return new Date(b.date).getTime() - new Date(a.date).getTime()
        case "duration":
          return b.duration.localeCompare(a.duration)
        case "client":
          return a.clientName.localeCompare(b.clientName)
        default:
          return 0
      }
    })
    setCalls(sorted)
  }

  const filteredCalls = calls.filter(call => {
    // Filter by client name
    const matchesSearch = call.clientName.toLowerCase().includes(searchQuery.toLowerCase())
    
    // Filter by date range
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
        {/* Фильтры и поиск */}
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
              <Select value={sortBy} onValueChange={handleSort}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Сортировка" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="duration">По длительности</SelectItem>
                  <SelectItem value="client">По имени клиента</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Список звонков */}
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
                        {call.date}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {call.duration}
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

        {filteredCalls.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center text-neutral-500">
              Звонки не найдены
            </CardContent>
          </Card>
        )}
      </div>

      {/* Диалог с деталями звонка - 80% размера страницы */}
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
                  <p className="font-medium">{selectedCall.date}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Длительность</p>
                  <p className="font-medium">{selectedCall.duration}</p>
                </div>
              </div>

              {/* Аудио файл */}
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

              {/* Транскрипт в стиле аналитика */}
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
