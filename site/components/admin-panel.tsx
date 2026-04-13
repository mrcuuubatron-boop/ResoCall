"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { LogOut } from "lucide-react"
import { loadModuleSettings, saveModuleSettings } from "@/lib/module-settings"

interface AdminPanelProps {
  onLogout: () => void
  login: string
  password: string
}

const mockCurrentLogs = [
  "[2026-02-25 14:32:15] Модель загружена успешно",
  "[2026-02-25 14:32:18] Инициализация ASR модуля...",
  "[2026-02-25 14:32:22] ASR модуль готов к работе",
  "[2026-02-25 14:33:01] Обработка звонка #1847",
  "[2026-02-25 14:33:05] Распознавание речи: 98.2%",
  "[2026-02-25 14:33:08] Сентимент-анализ: нейтральный",
  "[2026-02-25 14:33:10] Классификация: техническая проблема",
  "[2026-02-25 14:33:12] Соответствие скрипту: 92%",
  "[2026-02-25 14:35:44] Обработка звонка #1848",
  "[2026-02-25 14:35:48] Распознавание речи: 95.7%",
  "[2026-02-25 14:35:51] Сентимент-анализ: негативный",
  "[2026-02-25 14:35:54] Классификация: проблемы с оплатой",
  "[2026-02-25 14:36:02] Обработка звонка #1849",
  "[2026-02-25 14:36:08] Распознавание речи: 97.1%",
  "[2026-02-25 14:36:11] Сентимент-анализ: позитивный",
  "[2026-02-25 14:36:15] Классификация: консультация",
  "[2026-02-25 14:36:18] Соответствие скрипту: 96%",
  "[2026-02-25 14:38:22] Обработка звонка #1850",
  "[2026-02-25 14:38:25] Распознавание речи: 94.3%",
]

const mockPreviousLaunches = [
  {
    id: 1,
    date: "25.02.2026 14:30",
    status: "active",
    processed: 156,
    errors: 3,
  },
  {
    id: 2,
    date: "24.02.2026 09:00",
    status: "completed",
    processed: 842,
    errors: 12,
  },
  {
    id: 3,
    date: "23.02.2026 09:00",
    status: "completed",
    processed: 798,
    errors: 8,
  },
  {
    id: 4,
    date: "22.02.2026 09:00",
    status: "error",
    processed: 234,
    errors: 45,
  },
  {
    id: 5,
    date: "21.02.2026 09:00",
    status: "completed",
    processed: 876,
    errors: 5,
  },
]

const mockErrorStats = {
  total: 73,
  byType: [
    { type: "Timeout при обработке аудио", count: 23, percentage: 31.5 },
    { type: "Низкое качество записи", count: 28, percentage: 38.4 },
    { type: "Ошибка классификации", count: 12, percentage: 16.4 },
    { type: "Превышен лимит памяти", count: 6, percentage: 8.2 },
    { type: "Ошибка подключения к БД", count: 4, percentage: 5.5 },
  ],
}

type ViewType = "main" | "history" | "errors"

export function AdminPanel({ onLogout, login, password }: AdminPanelProps) {
  const [currentView, setCurrentView] = useState<ViewType>("main")
  const [isRunning, setIsRunning] = useState(true)
  const [isSettingsReady, setIsSettingsReady] = useState(false)

  useEffect(() => {
    let active = true
    void loadModuleSettings("admin", login, password)
      .then((payload) => {
        if (!active) {
          return
        }
        const savedView = payload.settings.currentView
        if (savedView === "main" || savedView === "history" || savedView === "errors") {
          setCurrentView(savedView)
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
    void saveModuleSettings("admin", { currentView }, login, password)
  }, [currentView, isSettingsReady, login, password])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-green-400"
      case "completed": return "text-blue-400"
      case "error": return "text-red-400"
      default: return "text-zinc-400"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "active": return "Активен"
      case "completed": return "Завершён"
      case "error": return "Ошибка"
      default: return status
    }
  }

  // Шапка
  const Header = () => (
    <header className="bg-zinc-900 border-b border-zinc-700 p-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">ResoCall</h1>
          <p className="text-zinc-400 text-sm">Администратор</p>
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

  // Страница "История предыдущих запусков"
  if (currentView === "history") {
    return (
      <div className="flex-1 flex flex-col bg-zinc-800">
        <Header />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <div className="bg-zinc-700 rounded-lg p-6 h-full">
            <h2 className="text-xl font-medium mb-6 text-white text-center">История предыдущих запусков</h2>
            
            <Button
              onClick={() => setCurrentView("main")}
              className="bg-zinc-600 hover:bg-zinc-500 text-white mb-6"
            >
              Назад
            </Button>

            <div className="bg-zinc-600 rounded-lg p-4 max-h-[500px] overflow-y-auto">
              {mockPreviousLaunches.map((launch) => (
                <div
                  key={launch.id}
                  className="flex justify-between items-center p-4 border-b border-zinc-500 last:border-0"
                >
                  <div>
                    <div className="text-white font-medium text-lg">Запуск #{launch.id}</div>
                    <div className="text-zinc-400">{launch.date}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium text-lg ${getStatusColor(launch.status)}`}>
                      {getStatusText(launch.status)}
                    </div>
                    <div className="text-zinc-400">
                      Обработано: {launch.processed} | Ошибок: {launch.errors}
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

  // Страница "Статистика ошибок"
  if (currentView === "errors") {
    return (
      <div className="flex-1 flex flex-col bg-zinc-800">
        <Header />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <div className="bg-zinc-700 rounded-lg p-6 h-full">
            <h2 className="text-xl font-medium mb-6 text-white text-center">Статистика ошибок за все запуски</h2>
            
            <Button
              onClick={() => setCurrentView("main")}
              className="bg-zinc-600 hover:bg-zinc-500 text-white mb-6"
            >
              Назад
            </Button>

            <div className="bg-zinc-600 rounded-lg p-6">
              <div className="text-white font-medium text-xl mb-6">
                Всего ошибок: <span className="text-red-400">{mockErrorStats.total}</span>
              </div>
              
              <div className="space-y-4">
                {mockErrorStats.byType.map((error, index) => (
                  <div key={index} className="bg-zinc-700 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-zinc-200">{error.type}</span>
                      <span className="text-red-400 font-medium text-lg">{error.count}</span>
                    </div>
                    <div className="w-full bg-zinc-800 rounded-full h-3">
                      <div
                        className="bg-red-500 h-3 rounded-full transition-all"
                        style={{ width: `${error.percentage}%` }}
                      />
                    </div>
                    <div className="text-right text-zinc-400 text-sm mt-1">
                      {error.percentage}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  // Главная страница администратора
  return (
    <div className="flex-1 flex flex-col bg-zinc-800">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        <div className="bg-zinc-700 rounded-lg p-6 h-full">
          {/* Кнопки навигации */}
          <div className="flex gap-3 mb-6">
            <Button
              onClick={() => setCurrentView("history")}
              className="bg-white text-zinc-800 hover:bg-zinc-100"
            >
              Логи предыдущих запусков
            </Button>
            <Button
              onClick={() => setCurrentView("errors")}
              className="bg-white text-zinc-800 hover:bg-zinc-100"
            >
              Статистика ошибок
            </Button>
          </div>

          <div className="grid grid-cols-[1fr_160px] gap-6">
            {/* Левая часть - логи текущего запуска */}
            <div className="bg-zinc-600 rounded-lg p-6 min-h-[400px]">
              <div className="text-lg text-zinc-200 mb-4">
                Логи текущего/последнего запуска:
                {isRunning && (
                  <span className="ml-3 inline-flex items-center">
                    <span className="animate-pulse w-2.5 h-2.5 bg-green-500 rounded-full mr-2"></span>
                    <span className="text-green-400">Активен</span>
                  </span>
                )}
              </div>
              <div className="space-y-1 max-h-[350px] overflow-y-auto font-mono text-sm text-green-400 bg-zinc-800 rounded-lg p-4">
                {mockCurrentLogs.map((log, index) => (
                  <div key={index} className="py-0.5 hover:bg-zinc-700 px-2 rounded">
                    {log}
                  </div>
                ))}
              </div>
            </div>

            {/* Правая часть - кнопки управления */}
            <div className="bg-red-800/80 rounded-lg p-4 flex flex-col gap-3">
              <div className="text-white font-medium mb-2 text-center">Управление</div>
              {isRunning ? (
                <>
                  <Button
                    onClick={() => setIsRunning(false)}
                    className="bg-red-600 hover:bg-red-700 text-white"
                  >
                    Стоп
                  </Button>
                  <Button
                    className="bg-yellow-600 hover:bg-yellow-700 text-white"
                  >
                    Пауза
                  </Button>
                </>
              ) : (
                <Button
                  onClick={() => setIsRunning(true)}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  Запуск
                </Button>
              )}
              <Button
                className="bg-zinc-600 hover:bg-zinc-700 text-white"
              >
                Перезапуск
              </Button>
              <Button
                className="bg-zinc-600 hover:bg-zinc-700 text-white"
              >
                Настройки
              </Button>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
