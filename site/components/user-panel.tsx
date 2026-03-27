"use client"

import { useState } from "react"
import DashboardLayout from "./dashboard-layout"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Search, Clock, Calendar } from "lucide-react"

interface Call {
  id: string
  clientName: string
  date: string
  duration: string
  sentiment: "positive" | "neutral" | "negative"
  transcript: string
  category: string
}

const mockCalls: Call[] = [
  {
    id: "1",
    clientName: "Иванов Иван",
    date: "2026-03-20 10:30",
    duration: "5:23",
    sentiment: "positive",
    transcript: "Оператор: Добрый день! Меня зовут Анна. Чем могу помочь?\nКлиент: Здравствуйте! Хочу узнать о новых тарифах.\nОператор: С удовольствием расскажу! У нас есть несколько выгодных предложений...\nКлиент: Отлично, расскажите подробнее.\nОператор: Конечно! Первый тариф включает безлимитные звонки...",
    category: "Консультация"
  },
  {
    id: "2",
    clientName: "Петрова Мария",
    date: "2026-03-20 09:15",
    duration: "8:45",
    sentiment: "negative",
    transcript: "Оператор: Добрый день! Меня зовут Анна. Чем могу помочь?\nКлиент: У меня проблема с оплатой, уже третий день не могу оплатить счет!\nОператор: Понимаю ваше беспокойство. Давайте разберемся...\nКлиент: Я уже звонил вчера, мне обещали перезвонить!\nОператор: Приношу извинения за задержку. Сейчас проверю статус вашего обращения...",
    category: "Проблемы с оплатой"
  },
  {
    id: "3",
    clientName: "Сидоров Петр",
    date: "2026-03-19 16:20",
    duration: "3:12",
    sentiment: "neutral",
    transcript: "Оператор: Добрый день! Меня зовут Анна. Чем могу помочь?\nКлиент: Добрый день, подскажите режим работы вашего офиса.\nОператор: Конечно! Наш офис работает с понедельника по пятницу с 9:00 до 18:00.\nКлиент: А в субботу?\nОператор: В субботу мы работаем с 10:00 до 15:00.",
    category: "Общая информация"
  },
  {
    id: "4",
    clientName: "Ковалев Александр",
    date: "2026-03-19 14:05",
    duration: "12:30",
    sentiment: "negative",
    transcript: "Оператор: Добрый день! Меня зовут Анна. Чем могу помочь?\nКлиент: У меня серьезная техническая проблема, интернет не работает уже 2 дня!\nОператор: Очень извиняюсь за неудобства. Давайте срочно разберемся...\nКлиент: Я работаю из дома, мне срочно нужен интернет!\nОператор: Понимаю критичность ситуации. Сейчас создам заявку с высоким приоритетом...",
    category: "Техническая неисправность"
  },
  {
    id: "5",
    clientName: "Новикова Елена",
    date: "2026-03-18 11:45",
    duration: "6:18",
    sentiment: "positive",
    transcript: "Оператор: Добрый день! Меня зовут Анна. Чем могу помочь?\nКлиент: Здравствуйте! Хочу поблагодарить вашу компанию за быстрое решение моей проблемы!\nОператор: Спасибо за ваш отзыв! Мы рады, что смогли помочь.\nКлиент: Техник приехал вовремя и все починил за час.\nОператор: Передам благодарность нашей технической службе!",
    category: "Благодарность"
  },
]

interface UserPanelProps {
  onLogout: () => void
}

export function UserPanel({ onLogout }: UserPanelProps) {
  const [calls, setCalls] = useState<Call[]>(mockCalls)
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState<string>("date")
  const [selectedCall, setSelectedCall] = useState<Call | null>(null)
  const [searchInDialog, setSearchInDialog] = useState("")

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

  const filteredCalls = calls.filter(call =>
    call.clientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    call.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "bg-green-100 text-green-800 border-green-200"
      case "negative":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-neutral-100 text-neutral-800 border-neutral-200"
    }
  }

  const getSentimentLabel = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "Позитивный"
      case "negative":
        return "Негативный"
      default:
        return "Нейтральный"
    }
  }

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
                  placeholder="Поиск по имени клиента или категории..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={sortBy} onValueChange={handleSort}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Сортировка" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">По дате</SelectItem>
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
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-medium">{call.clientName}</h3>
                      <Badge variant="outline" className={getSentimentColor(call.sentiment)}>
                        {getSentimentLabel(call.sentiment)}
                      </Badge>
                      <Badge variant="outline">{call.category}</Badge>
                    </div>
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

      {/* Диалог с деталями звонка */}
      <Dialog open={!!selectedCall} onOpenChange={() => setSelectedCall(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Детали звонка</DialogTitle>
          </DialogHeader>
          {selectedCall && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-neutral-500">Клиент</p>
                  <p className="font-medium">{selectedCall.clientName}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Категория</p>
                  <p className="font-medium">{selectedCall.category}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Дата и время</p>
                  <p className="font-medium">{selectedCall.date}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Длительность</p>
                  <p className="font-medium">{selectedCall.duration}</p>
                </div>
                <div>
                  <p className="text-sm text-neutral-500">Настроение</p>
                  <Badge className={getSentimentColor(selectedCall.sentiment)}>
                    {getSentimentLabel(selectedCall.sentiment)}
                  </Badge>
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

              <div>
                <p className="text-sm text-neutral-500 mb-2">Транскрипт разговора</p>
                <div className="bg-neutral-50 p-4 rounded-lg whitespace-pre-line text-sm">
                  {highlightText(selectedCall.transcript, searchInDialog)}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
