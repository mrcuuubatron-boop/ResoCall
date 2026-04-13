"use client"

import { useEffect, useMemo, useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LogOut } from "lucide-react"
import { loadModuleSettings, saveModuleSettings } from "@/lib/module-settings"

interface UserPanelProps {
  onLogout: () => void
  login: string
  password: string
}

const mockCalls = [
  { id: 1, date: "25.02.26", name: "Петров В.А", duration: 245 },
  { id: 2, date: "25.02.26", name: "Иванов Г.Н", duration: 312 },
  { id: 3, date: "24.02.26", name: "Климов П.Т", duration: 189 },
  { id: 4, date: "24.02.26", name: "Сидорова А.М", duration: 421 },
  { id: 5, date: "23.02.26", name: "Козлов И.В", duration: 156 },
  { id: 6, date: "23.02.26", name: "Морозова Е.С", duration: 278 },
  { id: 7, date: "22.02.26", name: "Волков Д.А", duration: 367 },
]

const mockDialogs: Record<number, string[]> = {
  1: [
    "-Здравствуйте!",
    "-Здравствуйте! (Петров В.А)",
    "-Что вас беспокоит?",
    "-У меня проблема с оплатой услуг.",
    "-Сейчас проверю вашу учетную запись.",
    "-Хорошо, жду.",
    "-Вижу задолженность. Хотите оплатить сейчас?",
    "-Да, давайте.",
    "..."
  ],
  2: [
    "-Добрый день!",
    "-Добрый день! (Иванов Г.Н)",
    "-Чем могу помочь?",
    "-Хотел бы уточнить статус заявки.",
    "-Назовите номер заявки, пожалуйста.",
    "-Номер 45678.",
    "-Заявка в обработке, ожидайте ответа в течение суток.",
    "..."
  ],
  3: [
    "-Здравствуйте!",
    "-Здравствуйте! (Климов П.Т)",
    "-Слушаю вас.",
    "-Не работает интернет уже второй день.",
    "-Сейчас проверю линию.",
    "-Вижу проблему на нашей стороне.",
    "-Когда исправите?",
    "-В течение 2 часов.",
    "..."
  ],
  4: [
    "-Добрый день!",
    "-Добрый день! (Сидорова А.М)",
    "-Как я могу вам помочь?",
    "-Нужна консультация по тарифам.",
    "-Какой тариф вас интересует?",
    "-Безлимитный интернет.",
    "-У нас есть несколько вариантов...",
    "..."
  ],
  5: [
    "-Здравствуйте!",
    "-Здравствуйте! (Козлов И.В)",
    "-Чем могу быть полезен?",
    "-Хочу оформить дополнительную услугу.",
    "-Какую именно?",
    "-Антивирус.",
    "..."
  ],
  6: [
    "-Добрый день!",
    "-Добрый день! (Морозова Е.С)",
    "-Слушаю вас.",
    "-Хочу расторгнуть договор.",
    "-Причина расторжения?",
    "-Переезжаю в другой город.",
    "..."
  ],
  7: [
    "-Здравствуйте!",
    "-Здравствуйте! (Волков Д.А)",
    "-Чем могу помочь?",
    "-Вопрос по счету за прошлый месяц.",
    "-Слушаю вас внимательно.",
    "..."
  ],
}

type SortType = "date_desc" | "date_asc" | "duration_desc" | "duration_asc" | "name_asc" | "name_desc"

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, "0")}`
}

export function UserPanel({ onLogout, login, password }: UserPanelProps) {
  const [searchArchive, setSearchArchive] = useState("")
  const [searchDialog, setSearchDialog] = useState("")
  const [selectedCall, setSelectedCall] = useState<number | null>(1)
  const [sortBy, setSortBy] = useState<SortType>("date_desc")
  const [isSettingsReady, setIsSettingsReady] = useState(false)

  useEffect(() => {
    let active = true
    void loadModuleSettings("user", login, password)
      .then((payload) => {
        if (!active) {
          return
        }
        const savedSortBy = payload.settings.sortBy
        if (
          savedSortBy === "date_desc" ||
          savedSortBy === "date_asc" ||
          savedSortBy === "duration_desc" ||
          savedSortBy === "duration_asc" ||
          savedSortBy === "name_asc" ||
          savedSortBy === "name_desc"
        ) {
          setSortBy(savedSortBy)
        }
      })
      .finally(() => {
        if (active) {
          setIsSettingsReady(true)
        }
      })

    return () => {
      active = false
    }
  }, [login, password])

  useEffect(() => {
    if (!isSettingsReady) {
      return
    }
    void saveModuleSettings("user", { sortBy }, login, password)
  }, [sortBy, isSettingsReady, login, password])

  const filteredAndSortedCalls = useMemo(() => {
    let result = mockCalls.filter(
      (call) =>
        call.name.toLowerCase().includes(searchArchive.toLowerCase()) ||
        call.date.includes(searchArchive)
    )

    result.sort((a, b) => {
      switch (sortBy) {
        case "date_desc":
          return b.date.localeCompare(a.date)
        case "date_asc":
          return a.date.localeCompare(b.date)
        case "duration_desc":
          return b.duration - a.duration
        case "duration_asc":
          return a.duration - b.duration
        case "name_asc":
          return a.name.localeCompare(b.name)
        case "name_desc":
          return b.name.localeCompare(a.name)
        default:
          return 0
      }
    })

    return result
  }, [searchArchive, sortBy])

  const currentDialog = selectedCall ? mockDialogs[selectedCall] || [] : []
  
  const filteredDialog = useMemo(() => {
    if (!searchDialog) return currentDialog
    return currentDialog.filter((line) =>
      line.toLowerCase().includes(searchDialog.toLowerCase())
    )
  }, [currentDialog, searchDialog])

  const highlightText = (text: string, search: string) => {
    if (!search) return text
    const regex = new RegExp(`(${search})`, "gi")
    const parts = text.split(regex)
    return parts.map((part, i) =>
      regex.test(part) ? (
        <span key={i} className="bg-yellow-300 text-black">{part}</span>
      ) : (
        part
      )
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-zinc-800">
      {/* Шапка */}
      <header className="bg-zinc-900 border-b border-zinc-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">ResoCall</h1>
            <p className="text-zinc-400 text-sm">Пользователь (работник)</p>
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

      {/* Основной контент */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        <div className="bg-white rounded-lg p-6 h-full">
          {/* Верхняя панель с поиском */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            <div className="flex gap-2">
              <Input
                placeholder="Поиск диалогов в архиве"
                value={searchArchive}
                onChange={(e) => setSearchArchive(e.target.value)}
                className="flex-1"
              />
              <Select value={sortBy} onValueChange={(val) => setSortBy(val as SortType)}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Сортировка" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date_desc">По дате (новые)</SelectItem>
                  <SelectItem value="date_asc">По дате (старые)</SelectItem>
                  <SelectItem value="duration_desc">По длительности (убыв.)</SelectItem>
                  <SelectItem value="duration_asc">По длительности (возр.)</SelectItem>
                  <SelectItem value="name_asc">По имени (А-Я)</SelectItem>
                  <SelectItem value="name_desc">По имени (Я-А)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Input
              placeholder="Поиск слов в текущем диалоге"
              value={searchDialog}
              onChange={(e) => setSearchDialog(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Левая колонка - Архив звонков */}
            <div className="border border-zinc-300 rounded-lg p-4">
              <div className="font-medium mb-3 text-zinc-700">Архив звонков</div>
              <div className="space-y-1 max-h-[500px] overflow-y-auto">
                {filteredAndSortedCalls.map((call) => (
                  <div
                    key={call.id}
                    onClick={() => setSelectedCall(call.id)}
                    className={`p-3 rounded cursor-pointer transition-colors flex justify-between items-center ${
                      selectedCall === call.id
                        ? "bg-zinc-200 text-zinc-900"
                        : "hover:bg-zinc-100 text-zinc-700"
                    }`}
                  >
                    <span>{call.date} {call.name}</span>
                    <span className="text-zinc-500">{formatDuration(call.duration)}</span>
                  </div>
                ))}
                {filteredAndSortedCalls.length === 0 && (
                  <div className="text-zinc-400 text-center py-8">
                    Диалоги не найдены
                  </div>
                )}
              </div>
            </div>

            {/* Правая колонка - Текст диалога */}
            <div className="border border-zinc-300 rounded-lg p-4">
              <div className="font-medium mb-3 text-zinc-700">
                Текст выбранного диалога
                {searchDialog && (
                  <span className="text-zinc-500 font-normal ml-2">
                    (найдено: {filteredDialog.length})
                  </span>
                )}
              </div>
              <div className="space-y-2 max-h-[500px] overflow-y-auto text-zinc-700">
                {selectedCall ? (
                  filteredDialog.length > 0 ? (
                    filteredDialog.map((line, index) => (
                      <div key={index} className="py-1">
                        {highlightText(line, searchDialog)}
                      </div>
                    ))
                  ) : (
                    <div className="text-zinc-400 text-center py-8">
                      Совпадений не найдено
                    </div>
                  )
                ) : (
                  <div className="text-zinc-400 text-center py-8">
                    Выберите диалог из архива
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Футер */}
      <footer className="bg-zinc-900 border-t border-zinc-700 p-4 text-center text-zinc-500 text-sm">
        <p>Проект "ResoCall" — ООО "Неосистемы ИТ" | Заказчик: Дибров Иван Васильевич</p>
      </footer>
    </div>
  )
}
