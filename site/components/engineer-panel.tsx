"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LogOut } from "lucide-react"

interface EngineerPanelProps {
  onLogout: () => void
}

const mockEmployees = [
  { id: 1, name: "Петров В.А", calls: 45, rating: 4.5 },
  { id: 2, name: "Иванов Г.Н", calls: 38, rating: 4.2 },
  { id: 3, name: "Климов П.Т", calls: 52, rating: 4.8 },
  { id: 4, name: "Сидорова А.М", calls: 41, rating: 4.3 },
  { id: 5, name: "Козлов И.В", calls: 33, rating: 3.9 },
]

const mockDialogStats = [
  { id: 234, employee: "Иванов В.В", sentiment: "нейтральный", scriptScore: 92, wordCount: 156, duration: "4:32" },
  { id: 235, employee: "Петров В.А", sentiment: "позитивный", scriptScore: 95, wordCount: 203, duration: "5:18" },
  { id: 236, employee: "Климов П.Т", sentiment: "негативный", scriptScore: 78, wordCount: 312, duration: "7:45" },
  { id: 237, employee: "Сидорова А.М", sentiment: "нейтральный", scriptScore: 88, wordCount: 178, duration: "4:56" },
  { id: 238, employee: "Козлов И.В", sentiment: "позитивный", scriptScore: 91, wordCount: 145, duration: "3:42" },
]

const mockUnprocessedCalls = [
  { id: 1001, date: "25.02.26 14:32", employee: "Петров В.А", reason: "Низкое качество аудио" },
  { id: 1002, date: "25.02.26 15:18", employee: "Иванов Г.Н", reason: "Ошибка распознавания" },
  { id: 1003, date: "24.02.26 11:45", employee: "Климов П.Т", reason: "Timeout обработки" },
]

const mockEmployeeDialogs: Record<number, { id: number; date: string; client: string; sentiment: string }[]> = {
  1: [
    { id: 101, date: "25.02.26", client: "Клиент А", sentiment: "позитивный" },
    { id: 102, date: "24.02.26", client: "Клиент Б", sentiment: "нейтральный" },
  ],
  2: [
    { id: 201, date: "25.02.26", client: "Клиент В", sentiment: "негативный" },
    { id: 202, date: "23.02.26", client: "Клиент Г", sentiment: "позитивный" },
  ],
  3: [
    { id: 301, date: "25.02.26", client: "Клиент Д", sentiment: "позитивный" },
    { id: 302, date: "25.02.26", client: "Клиент Е", sentiment: "нейтральный" },
    { id: 303, date: "24.02.26", client: "Клиент Ж", sentiment: "позитивный" },
  ],
  4: [
    { id: 401, date: "24.02.26", client: "Клиент З", sentiment: "нейтральный" },
  ],
  5: [
    { id: 501, date: "23.02.26", client: "Клиент И", sentiment: "негативный" },
    { id: 502, date: "22.02.26", client: "Клиент К", sentiment: "позитивный" },
  ],
}

type ViewType = "main" | "dialogStats" | "employees" | "unprocessed" | "employeeDialogs"

export function EngineerPanel({ onLogout }: EngineerPanelProps) {
  const [currentView, setCurrentView] = useState<ViewType>("main")
  const [period, setPeriod] = useState("day")
  const [sortBy, setSortBy] = useState("date")
  const [showCalendar, setShowCalendar] = useState(false)
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date())
  const [selectedEmployee, setSelectedEmployee] = useState<typeof mockEmployees[0] | null>(null)

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "позитивный": return "text-green-600 bg-green-100"
      case "негативный": return "text-red-600 bg-red-100"
      default: return "text-yellow-600 bg-yellow-100"
    }
  }

  const handleBack = () => {
    if (currentView === "employeeDialogs") {
      setCurrentView("employees")
      setSelectedEmployee(null)
    } else {
      setCurrentView("main")
    }
  }

  const handleEmployeeClick = (employee: typeof mockEmployees[0]) => {
    setSelectedEmployee(employee)
    setCurrentView("employeeDialogs")
  }

  // Шапка (общая для всех страниц)
  const Header = () => (
    <header className="bg-zinc-900 border-b border-zinc-700 p-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">ResoCall</h1>
          <p className="text-zinc-400 text-sm">Инженер отдела качества</p>
        </div>
        <Button
          onClick={onLogout}
          variant="outline"
          className="border-zinc-600 text-zinc-300 hover:bg-zinc-700"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Выйти
        </Button>
      </div>
    </header>
  )

  // Футер
  const Footer = () => (
    <footer className="bg-zinc-900 border-t border-zinc-700 p-4 text-center text-zinc-500 text-sm">
      <p>Проект "ResoCall" — ООО "Неосистемы ИТ" | Заказчик: Дибров Иван Васильевич</p>
    </footer>
  )

  // Страница "Статистика каждого диалога"
  if (currentView === "dialogStats") {
    return (
      <div className="flex-1 flex flex-col bg-zinc-800">
        <Header />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <div className="bg-zinc-700 rounded-lg p-6 h-full">
            <h2 className="text-xl font-medium mb-6 text-white text-center">Статистика каждого диалога</h2>
            
            <div className="flex gap-3 mb-6 flex-wrap">
              <Button
                onClick={handleBack}
                className="bg-zinc-600 hover:bg-zinc-500 text-white"
              >
                Назад
              </Button>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-[160px] bg-zinc-600 border-zinc-500 text-white">
                  <SelectValue placeholder="Сортировка" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">По дате</SelectItem>
                  <SelectItem value="sentiment">По настроению</SelectItem>
                  <SelectItem value="script">По скрипту</SelectItem>
                </SelectContent>
              </Select>
              <Select value={period} onValueChange={setPeriod}>
                <SelectTrigger className="w-[180px] bg-zinc-600 border-zinc-500 text-white">
                  <SelectValue placeholder="Промежуток времени" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="day">День</SelectItem>
                  <SelectItem value="week">Неделя</SelectItem>
                  <SelectItem value="month">Месяц</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="bg-white rounded-lg p-4 max-h-[500px] overflow-y-auto">
              {mockDialogStats.map((dialog) => (
                <div key={dialog.id} className="mb-6 last:mb-0">
                  <div className="bg-zinc-100 rounded p-3 mb-2">
                    <span className="font-medium text-zinc-800">
                      Диалог № {dialog.id} Сотрудник: {dialog.employee}
                    </span>
                  </div>
                  <div className="bg-yellow-200 rounded p-4 text-zinc-800">
                    <div className="font-medium mb-3">Краткая статистика (диаграммы, подсчёт слов, настроение)</div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>Настроение: <span className={`px-2 py-0.5 rounded ${getSentimentColor(dialog.sentiment)}`}>{dialog.sentiment}</span></div>
                      <div>Соответствие скрипту: {dialog.scriptScore}%</div>
                      <div>Количество слов: {dialog.wordCount}</div>
                      <div>Длительность: {dialog.duration}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  // Страница "Список сотрудников"
  if (currentView === "employees") {
    return (
      <div className="flex-1 flex flex-col bg-zinc-800">
        <Header />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <div className="bg-zinc-700 rounded-lg p-6 h-full">
            <h2 className="text-xl font-medium mb-6 text-white text-center">Список сотрудников</h2>
            
            <Button
              onClick={handleBack}
              className="bg-zinc-600 hover:bg-zinc-500 text-white mb-6"
            >
              Назад
            </Button>

            <div className="bg-white rounded-lg p-4 max-h-[500px] overflow-y-auto">
              {mockEmployees.map((emp) => (
                <div
                  key={emp.id}
                  onClick={() => handleEmployeeClick(emp)}
                  className="flex justify-between items-center p-4 border-b border-zinc-200 last:border-0 hover:bg-zinc-50 cursor-pointer transition-colors"
                >
                  <span className="font-medium text-zinc-800 text-lg">{emp.name}</span>
                  <div className="flex gap-6 text-sm">
                    <span className="text-zinc-600">Звонков: {emp.calls}</span>
                    <span className={`font-medium ${emp.rating >= 4.5 ? "text-green-600" : emp.rating >= 4.0 ? "text-yellow-600" : "text-red-600"}`}>
                      Рейтинг: {emp.rating}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  // Страница диалогов сотрудника
  if (currentView === "employeeDialogs" && selectedEmployee) {
    const dialogs = mockEmployeeDialogs[selectedEmployee.id] || []
    return (
      <div className="flex-1 flex flex-col bg-zinc-800">
        <Header />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <div className="bg-zinc-700 rounded-lg p-6 h-full">
            <h2 className="text-xl font-medium mb-6 text-white text-center">
              Диалоги сотрудника: {selectedEmployee.name}
            </h2>
            
            <Button
              onClick={handleBack}
              className="bg-zinc-600 hover:bg-zinc-500 text-white mb-6"
            >
              Назад
            </Button>

            <div className="bg-white rounded-lg p-4 max-h-[500px] overflow-y-auto">
              {dialogs.length > 0 ? (
                dialogs.map((dialog) => (
                  <div
                    key={dialog.id}
                    className="flex justify-between items-center p-4 border-b border-zinc-200 last:border-0"
                  >
                    <div>
                      <span className="font-medium text-zinc-800">Диалог #{dialog.id}</span>
                      <span className="text-zinc-500 ml-3">{dialog.date}</span>
                    </div>
                    <div className="flex gap-6 text-sm">
                      <span className="text-zinc-600">{dialog.client}</span>
                      <span className={`px-2 py-0.5 rounded ${getSentimentColor(dialog.sentiment)}`}>
                        {dialog.sentiment}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-zinc-500 text-center py-8">Нет диалогов</div>
              )}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  // Страница "Необработанные звонки"
  if (currentView === "unprocessed") {
    return (
      <div className="flex-1 flex flex-col bg-zinc-800">
        <Header />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <div className="bg-zinc-700 rounded-lg p-6 h-full">
            <h2 className="text-xl font-medium mb-6 text-white text-center">Необработанные звонки</h2>
            
            <Button
              onClick={handleBack}
              className="bg-zinc-600 hover:bg-zinc-500 text-white mb-6"
            >
              Назад
            </Button>

            <div className="bg-white rounded-lg p-4 max-h-[500px] overflow-y-auto">
              {mockUnprocessedCalls.length > 0 ? (
                mockUnprocessedCalls.map((call) => (
                  <div
                    key={call.id}
                    className="flex justify-between items-center p-4 border-b border-zinc-200 last:border-0"
                  >
                    <div>
                      <span className="font-medium text-zinc-800">Звонок #{call.id}</span>
                      <span className="text-zinc-500 ml-3">{call.date}</span>
                    </div>
                    <div className="flex gap-6 text-sm">
                      <span className="text-zinc-600">{call.employee}</span>
                      <span className="text-red-600">{call.reason}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-green-600 text-center py-8">Все звонки обработаны</div>
              )}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  // Главная страница инженера
  return (
    <div className="flex-1 flex flex-col bg-zinc-800">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        <div className="bg-zinc-700 rounded-lg p-6 h-full">
          {/* Кнопки навигации */}
          <div className="flex gap-3 mb-6 flex-wrap">
            <Button
              onClick={() => setCurrentView("dialogStats")}
              className="bg-white text-zinc-800 hover:bg-zinc-100"
            >
              Статистика диалогов
            </Button>
            <Button
              onClick={() => setCurrentView("employees")}
              className="bg-white text-zinc-800 hover:bg-zinc-100"
            >
              Список сотрудников
            </Button>
            <Button
              onClick={() => setCurrentView("unprocessed")}
              className="bg-white text-zinc-800 hover:bg-zinc-100"
            >
              Необработанные звонки
              {mockUnprocessedCalls.length > 0 && (
                <span className="ml-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {mockUnprocessedCalls.length}
                </span>
              )}
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Левая часть - статистика */}
            <div className="bg-zinc-600 rounded-lg p-6 min-h-[300px]">
              <div className="text-lg text-zinc-200 mb-4">
                Статистика за {period === "day" ? "последний день" : period === "week" ? "неделю" : "месяц"}:
              </div>
              <div className="space-y-3 text-zinc-200">
                <div>Всего звонков: {period === "day" ? 176 : period === "week" ? 1232 : 5280}</div>
                <div>Обработано успешно: {period === "day" ? 158 : period === "week" ? 1108 : 4752}</div>
                <div>Среднее время: {period === "day" ? "4:32" : period === "week" ? "4:45" : "4:28"}</div>
                <div>Негативных отзывов: {period === "day" ? 8 : period === "week" ? 56 : 240}</div>
                <div>Соблюдение скрипта: {period === "day" ? "89%" : period === "week" ? "87%" : "88%"}</div>
                <div>Необработанных: {mockUnprocessedCalls.length}</div>
              </div>
            </div>

            {/* Правая часть - фильтры */}
            <div className="space-y-4">
              <Select value={period} onValueChange={setPeriod}>
                <SelectTrigger className="bg-zinc-600 border-zinc-500 text-white">
                  <SelectValue placeholder="Период" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="day">День</SelectItem>
                  <SelectItem value="week">Неделя</SelectItem>
                  <SelectItem value="month">Месяц</SelectItem>
                </SelectContent>
              </Select>

              <Button
                variant="outline"
                onClick={() => setShowCalendar(!showCalendar)}
                className="w-full border-zinc-500 text-zinc-300 hover:bg-zinc-600"
              >
                {showCalendar ? "Скрыть календарь" : "Выбрать дату"}
              </Button>

              {showCalendar && (
                <div className="bg-white rounded-lg p-3">
                  <Calendar
                    mode="single"
                    selected={selectedDate}
                    onSelect={setSelectedDate}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
