"use client"

import { useState } from "react"
import DashboardLayout from "./dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, Users, MessageSquare, CheckCircle, AlertCircle } from "lucide-react"

interface Employee {
  id: string
  name: string
  callsCount: number
  scriptCompliance: number
  avgSentiment: number
  rating: number
}

const mockEmployees: Employee[] = [
  { id: "1", name: "Анна Иванова", callsCount: 145, scriptCompliance: 95, avgSentiment: 85, rating: 4.8 },
  { id: "2", name: "Петр Сидоров", callsCount: 132, scriptCompliance: 88, avgSentiment: 78, rating: 4.5 },
  { id: "3", name: "Мария Петрова", callsCount: 128, scriptCompliance: 92, avgSentiment: 82, rating: 4.6 },
  { id: "4", name: "Дмитрий Козлов", callsCount: 119, scriptCompliance: 85, avgSentiment: 75, rating: 4.3 },
]

const sentimentData = [
  { name: "Позитивные", value: 425, color: "bg-green-500" },
  { name: "Нейтральные", value: 287, color: "bg-neutral-400" },
  { name: "Негативные", value: 112, color: "bg-red-500" },
]

const unprocessedCalls = [
  { id: "1", client: "Кузнецова А.И.", date: "2026-03-20 15:30", duration: "6:12", reason: "Низкое качество аудио" },
  { id: "2", client: "Смирнов П.П.", date: "2026-03-20 15:45", duration: "4:33", reason: "Timeout обработки" },
  { id: "3", client: "Новиков И.С.", date: "2026-03-20 16:10", duration: "8:21", reason: "Ошибка распознавания" },
]

interface EngineerPanelProps {
  onLogout: () => void
}

export function EngineerPanel({ onLogout }: EngineerPanelProps) {
  const [period, setPeriod] = useState<string>("week")

  const totalCalls = sentimentData.reduce((acc, item) => acc + item.value, 0)
  const avgScriptCompliance = Math.round(
    mockEmployees.reduce((acc, emp) => acc + emp.scriptCompliance, 0) / mockEmployees.length
  )

  return (
    <DashboardLayout title="Аналитика и статистика" role="Аналитик" onLogout={onLogout}>
      <div className="space-y-6">
        {/* Фильтр по периоду */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <span className="text-sm text-neutral-500">Период:</span>
              <Select value={period} onValueChange={setPeriod}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="day">День</SelectItem>
                  <SelectItem value="week">Неделя</SelectItem>
                  <SelectItem value="month">Месяц</SelectItem>
                  <SelectItem value="custom">Произвольная дата</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Общая статистика */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-500">Всего звонков</p>
                  <p className="text-2xl font-semibold mt-1">{totalCalls}</p>
                  <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>+12%</span>
                  </div>
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
                  <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>+3%</span>
                  </div>
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
                  <p className="text-2xl font-semibold mt-1">{mockEmployees.length}</p>
                  <div className="flex items-center gap-1 mt-2 text-sm text-neutral-500">
                    <span>Активных</span>
                  </div>
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
                  <div className="flex items-center gap-1 mt-2 text-sm text-amber-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>Требует обработки</span>
                  </div>
                </div>
                <AlertCircle className="w-10 h-10 text-neutral-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Распределение тональности */}
        <Card>
          <CardHeader>
            <CardTitle>Анализ тональности</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {sentimentData.map((item) => (
                <div key={item.name} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{item.name}</span>
                    <span className="font-medium">{item.value} ({Math.round(item.value / totalCalls * 100)}%)</span>
                  </div>
                  <div className="w-full bg-neutral-100 rounded-full h-3">
                    <div
                      className={`${item.color} h-3 rounded-full transition-all`}
                      style={{ width: `${(item.value / totalCalls) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Табы с данными */}
        <Tabs defaultValue="employees" className="space-y-4">
          <TabsList>
            <TabsTrigger value="employees">Рейтинг сотрудников</TabsTrigger>
            <TabsTrigger value="unprocessed">Необработанные звонки</TabsTrigger>
          </TabsList>

          <TabsContent value="employees" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Сотрудники Call-центра</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockEmployees.map((employee, index) => (
                    <div key={employee.id} className="border rounded-lg p-4 hover:bg-neutral-50 transition-colors cursor-pointer">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-neutral-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                            {index + 1}
                          </div>
                          <div>
                            <p className="font-medium">{employee.name}</p>
                            <p className="text-sm text-neutral-500">{employee.callsCount} звонков</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-sm">
                          {employee.rating}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-neutral-500">Соблюдение скрипта</span>
                            <span className="font-medium">{employee.scriptCompliance}%</span>
                          </div>
                          <Progress value={employee.scriptCompliance} className="h-2" />
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-neutral-500">Средняя тональность</span>
                            <span className="font-medium">{employee.avgSentiment}%</span>
                          </div>
                          <Progress value={employee.avgSentiment} className="h-2" />
                        </div>
                      </div>
                    </div>
                  ))}
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
                  {unprocessedCalls.map((call) => (
                    <div key={call.id} className="border rounded-lg p-4 flex items-center justify-between">
                      <div>
                        <p className="font-medium">{call.client}</p>
                        <p className="text-sm text-neutral-500">{call.date}</p>
                        <p className="text-sm text-red-600">{call.reason}</p>
                      </div>
                      <Badge variant="outline">{call.duration}</Badge>
                    </div>
                  ))}
                  {unprocessedCalls.length === 0 && (
                    <div className="text-center py-8 text-green-600">
                      Все звонки обработаны
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
