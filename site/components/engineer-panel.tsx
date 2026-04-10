"use client"

import { useState, useMemo } from "react"
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
import {
  calls,
  employees,
  getEmployeeById,
  getClientById,
  getCallsByDateRange,
  getUnprocessedCalls,
  calculateEmployeeRating,
  formatDuration,
  formatDate,
  getSentimentLabel,
  getSentimentColor,
  type Call,
  type Sentiment
} from "@/data/mock-data"

interface EngineerPanelProps {
  onLogout: () => void
}

export function EngineerPanel({ onLogout }: EngineerPanelProps) {
  // Состояние для главного календаря (по умолчанию последняя неделя)
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subDays(new Date(), 7),
    to: new Date()
  })
  
  // Состояние для фильтров в статистике диалогов
  const [dialogFilterDateRange, setDialogFilterDateRange] = useState<DateRange | undefined>()
  const [dialogFilterScript, setDialogFilterScript] = useState<string>("all")
  const [dialogFilterSentiment, setDialogFilterSentiment] = useState<string>("all")
  
  // Модальные окна
  const [selectedCall, setSelectedCall] = useState<Call | null>(null)
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null)
  const [unprocessedCallError, setUnprocessedCallError] = useState<Call | null>(null)
  
  // Сортировка рейтинга
  const [ratingSortAsc, setRatingSortAsc] = useState<boolean>(false)
  
  // Фильтрация звонков по выбранному периоду
  const filteredCalls = useMemo(() => {
    if (!dateRange?.from) return calls.filter(c => c.isProcessed)
    
    const start = startOfDay(dateRange.from)
    const end = dateRange.to ? endOfDay(dateRange.to) : endOfDay(dateRange.from)
    
    return getCallsByDateRange(start, end).filter(c => c.isProcessed)
  }, [dateRange])
  
  // Статистика по тональности
  const sentimentStats = useMemo(() => {
    const stats = { positive: 0, neutral: 0, negative: 0 }
    filteredCalls.forEach(call => {
      stats[call.sentiment]++
    })
    return stats
  }, [filteredCalls])
  
  const totalCalls = filteredCalls.length
  
  // Средний показатель соблюдения скрипта
  const avgScriptCompliance = useMemo(() => {
    if (filteredCalls.length === 0) return 0
    return Math.round(filteredCalls.reduce((acc, call) => acc + call.scriptCompliance, 0) / filteredCalls.length)
  }, [filteredCalls])
  
  // Рейтинг сотрудников
  const employeeRatings = useMemo(() => {
    const start = dateRange?.from ? startOfDay(dateRange.from) : undefined
    const end = dateRange?.to ? endOfDay(dateRange.to) : dateRange?.from ? endOfDay(dateRange.from) : undefined
    
    const ratings = employees.map(emp => ({
      ...emp,
      ...calculateEmployeeRating(emp.id, start, end)
    }))
    
    return ratingSortAsc 
      ? ratings.sort((a, b) => a.rating - b.rating)
      : ratings.sort((a, b) => b.rating - a.rating)
  }, [dateRange, ratingSortAsc])
  
  // Необработанные звонки
  const unprocessedCalls = getUnprocessedCalls()
  
  // Фильтрация диалогов для вкладки "Статистика диалогов"
  const dialogsFiltered = useMemo(() => {
    let result = calls.filter(c => c.isProcessed)
    
    // Фильтр по дате
    if (dialogFilterDateRange?.from) {
      const start = startOfDay(dialogFilterDateRange.from)
      const end = dialogFilterDateRange.to ? endOfDay(dialogFilterDateRange.to) : endOfDay(dialogFilterDateRange.from)
      result = result.filter(call => {
        const callDate = new Date(call.date)
        return callDate >= start && callDate <= end
      })
    }
    
    // Фильтр по скрипту
    if (dialogFilterScript !== "all") {
      if (dialogFilterScript === "gt90") {
        result = result.filter(c => c.scriptCompliance > 90)
      } else if (dialogFilterScript === "gt70") {
        result = result.filter(c => c.scriptCompliance > 70)
      } else if (dialogFilterScript === "lt70") {
        result = result.filter(c => c.scriptCompliance < 70)
      } else if (dialogFilterScript === "lt50") {
        result = result.filter(c => c.scriptCompliance < 50)
      }
    }
    
    // Фильтр по настроению
    if (dialogFilterSentiment !== "all") {
      result = result.filter(c => c.sentiment === dialogFilterSentiment)
    }
    
    return result
  }, [dialogFilterDateRange, dialogFilterScript, dialogFilterSentiment])
  
  // Звонки выбранного сотрудника
  const selectedEmployeeCalls = useMemo(() => {
    if (!selectedEmployeeId) return []
    return calls.filter(c => c.employeeId === selectedEmployeeId && c.isProcessed)
  }, [selectedEmployeeId])
  
  const selectedEmployee = selectedEmployeeId ? getEmployeeById(selectedEmployeeId) : null

  // Если выбран сотрудник - показываем его диалоги
  if (selectedEmployeeId && selectedEmployee) {
    return (
      <DashboardLayout title="Диалоги сотрудника" role="Аналитик" onLogout={onLogout}>
        <div className="space-y-6">
          <Button variant="outline" onClick={() => setSelectedEmployeeId(null)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
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
                    {selectedEmployeeCalls.length > 0 
                      ? Math.round(selectedEmployeeCalls.reduce((a, c) => a + c.scriptCompliance, 0) / selectedEmployeeCalls.length)
                      : 0}%
                  </p>
                  <p className="text-sm text-neutral-500">Соблюдение скрипта</p>
                </div>
                <div className="text-center p-4 bg-neutral-50 rounded-lg">
                  <p className="text-2xl font-bold">{calculateEmployeeRating(selectedEmployeeId).rating}</p>
                  <p className="text-sm text-neutral-500">Рейтинг</p>
                </div>
              </div>
              
              <div className="space-y-3">
                {selectedEmployeeCalls.map(call => {
                  const client = getClientById(call.clientId)
                  return (
                    <div 
                      key={call.id} 
                      className="border rounded-lg p-4 hover:bg-neutral-50 cursor-pointer transition-colors"
                      onClick={() => setSelectedCall(call)}
                    >
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
                          <Badge className={getSentimentColor(call.sentiment)}>
                            {getSentimentLabel(call.sentiment)}
                          </Badge>
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
        
        {/* Модальное окно диалога */}
        <CallDetailModal 
          call={selectedCall} 
          onClose={() => setSelectedCall(null)}
          onEmployeeClick={(empId) => {
            setSelectedCall(null)
            setSelectedEmployeeId(empId)
          }}
        />
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Аналитика и статистика" role="Аналитик" onLogout={onLogout}>
      <div className="space-y-6">
        {/* Выбор периода с календарём */}
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
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setDateRange({ from: new Date(), to: new Date() })}
                >
                  Сегодня
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setDateRange({ from: subDays(new Date(), 7), to: new Date() })}
                >
                  Неделя
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setDateRange({ from: subDays(new Date(), 30), to: new Date() })}
                >
                  Месяц
                </Button>
              </div>
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
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Позитивные</span>
                  <span className="font-medium">{sentimentStats.positive} ({totalCalls > 0 ? Math.round(sentimentStats.positive / totalCalls * 100) : 0}%)</span>
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-3">
                  <div
                    className="bg-green-500 h-3 rounded-full transition-all"
                    style={{ width: `${totalCalls > 0 ? (sentimentStats.positive / totalCalls) * 100 : 0}%` }}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Нейтральные</span>
                  <span className="font-medium">{sentimentStats.neutral} ({totalCalls > 0 ? Math.round(sentimentStats.neutral / totalCalls * 100) : 0}%)</span>
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-3">
                  <div
                    className="bg-neutral-400 h-3 rounded-full transition-all"
                    style={{ width: `${totalCalls > 0 ? (sentimentStats.neutral / totalCalls) * 100 : 0}%` }}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Негативные</span>
                  <span className="font-medium">{sentimentStats.negative} ({totalCalls > 0 ? Math.round(sentimentStats.negative / totalCalls * 100) : 0}%)</span>
                </div>
                <div className="w-full bg-neutral-100 rounded-full h-3">
                  <div
                    className="bg-red-500 h-3 rounded-full transition-all"
                    style={{ width: `${totalCalls > 0 ? (sentimentStats.negative / totalCalls) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Табы с данными */}
        <Tabs defaultValue="dialogs" className="space-y-4">
          <TabsList>
            <TabsTrigger value="dialogs">Статистика диалогов</TabsTrigger>
            <TabsTrigger value="employees">Рейтинг сотрудников</TabsTrigger>
            <TabsTrigger value="unprocessed">Необработанные звонки</TabsTrigger>
          </TabsList>

          {/* Статистика диалогов */}
          <TabsContent value="dialogs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Все диалоги</CardTitle>
              </CardHeader>
              <CardContent>
                {/* Фильтры */}
                <div className="flex flex-wrap gap-4 mb-6 pb-6 border-b">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-neutral-500">Дата:</span>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" size="sm">
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {dialogFilterDateRange?.from ? (
                            dialogFilterDateRange.to ? (
                              <>
                                {format(dialogFilterDateRange.from, "dd.MM", { locale: ru })} -{" "}
                                {format(dialogFilterDateRange.to, "dd.MM", { locale: ru })}
                              </>
                            ) : (
                              format(dialogFilterDateRange.from, "dd.MM.yyyy", { locale: ru })
                            )
                          ) : (
                            "Все даты"
                          )}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          initialFocus
                          mode="range"
                          selected={dialogFilterDateRange}
                          onSelect={setDialogFilterDateRange}
                          numberOfMonths={2}
                          locale={ru}
                        />
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
                      <SelectTrigger className="w-[160px]">
                        <SelectValue />
                      </SelectTrigger>
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
                      <SelectTrigger className="w-[160px]">
                        <SelectValue />
                      </SelectTrigger>
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
                    {dialogsFiltered.map(call => {
                      const employee = getEmployeeById(call.employeeId)
                      const client = getClientById(call.clientId)
                      return (
                        <div 
                          key={call.id} 
                          className="border rounded-lg p-4 hover:bg-neutral-50 transition-colors"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <button 
                              className="font-medium text-blue-600 hover:underline text-left"
                              onClick={() => setSelectedCall(call)}
                            >
                              Диалог #{call.id.replace('call-', '')}
                            </button>
                            <div className="flex items-center gap-2">
                              <Badge className={getSentimentColor(call.sentiment)}>
                                {getSentimentLabel(call.sentiment)}
                              </Badge>
                              <Badge variant="outline">{call.scriptCompliance}%</Badge>
                            </div>
                          </div>
                          <div className="text-sm text-neutral-500">
                            <span>Сотрудник: </span>
                            <button 
                              className="text-blue-600 hover:underline"
                              onClick={() => setSelectedEmployeeId(call.employeeId)}
                            >
                              {employee?.name}
                            </button>
                            <span> | Клиент: {client?.name}</span>
                          </div>
                          <div className="text-sm text-neutral-400 mt-1">
                            {formatDate(call.date)} | {formatDuration(call.duration)} | {call.category}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Рейтинг сотрудников */}
          <TabsContent value="employees" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Сотрудники Call-центра</CardTitle>
                    <p className="text-sm text-neutral-500 mt-1">
                      Рейтинг = 60% соблюдение скрипта + 40% средняя тональность (шкала 0-5)
                    </p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setRatingSortAsc(!ratingSortAsc)}
                  >
                    <ArrowUpDown className="w-4 h-4 mr-2" />
                    {ratingSortAsc ? "По возрастанию" : "По убыванию"}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {employeeRatings.map((employee, index) => (
                    <div key={employee.id} className="border rounded-lg p-4 hover:bg-neutral-50 transition-colors">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                            index === 0 ? 'bg-yellow-400 text-yellow-900' :
                            index === 1 ? 'bg-neutral-300 text-neutral-700' :
                            index === 2 ? 'bg-amber-600 text-white' :
                            'bg-neutral-900 text-white'
                          }`}>
                            {index + 1}
                          </div>
                          <div>
                            <button 
                              className="font-medium text-blue-600 hover:underline text-left"
                              onClick={() => setSelectedEmployeeId(employee.id)}
                            >
                              {employee.name}
                            </button>
                            <p className="text-sm text-neutral-500">{employee.callsCount} звонков</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-lg px-3 py-1">
                          {employee.rating}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-neutral-500">Соблюдение скрипта</span>
                            <span className="font-medium">{employee.avgScriptCompliance}%</span>
                          </div>
                          <Progress value={employee.avgScriptCompliance} className="h-2" />
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

          {/* Необработанные звонки */}
          <TabsContent value="unprocessed">
            <Card>
              <CardHeader>
                <CardTitle>Необработанные нейросетью звонки</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {unprocessedCalls.map((call) => {
                    const client = getClientById(call.clientId)
                    const employee = getEmployeeById(call.employeeId)
                    return (
                      <div key={call.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{client?.name}</p>
                            <p className="text-sm text-neutral-500">
                              Сотрудник: {employee?.name} | {formatDate(call.date)}
                            </p>
                            <button 
                              className="text-sm text-red-600 hover:underline mt-1"
                              onClick={() => setUnprocessedCallError(call)}
                            >
                              {call.errorReason}
                            </button>
                          </div>
                          <Badge variant="outline">{formatDuration(call.duration)}</Badge>
                        </div>
                      </div>
                    )
                  })}
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
      
      {/* Модальное окно диалога */}
      <CallDetailModal 
        call={selectedCall} 
        onClose={() => setSelectedCall(null)}
        onEmployeeClick={(empId) => {
          setSelectedCall(null)
          setSelectedEmployeeId(empId)
        }}
      />
      
      {/* Модальное окно ошибки необработанного звонка */}
      <Dialog open={!!unprocessedCallError} onOpenChange={() => setUnprocessedCallError(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ошибка обработки звонка</DialogTitle>
          </DialogHeader>
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
              <div>
                <p className="text-sm text-neutral-500 mb-2">Аудиофайл:</p>
                <a 
                  href={unprocessedCallError.audioUrl} 
                  className="text-blue-600 hover:underline flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  {unprocessedCallError.audioUrl}
                </a>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}

// Компонент модального окна с деталями диалога
function CallDetailModal({ 
  call, 
  onClose,
  onEmployeeClick 
}: { 
  call: Call | null
  onClose: () => void
  onEmployeeClick: (employeeId: string) => void
}) {
  if (!call) return null
  
  const employee = getEmployeeById(call.employeeId)
  const client = getClientById(call.clientId)
  
  return (
    <Dialog open={!!call} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Диалог #{call.id.replace('call-', '')}</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Информация о звонке */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="text-sm text-neutral-500">Сотрудник:</p>
              <button 
                className="font-medium text-blue-600 hover:underline"
                onClick={() => onEmployeeClick(call.employeeId)}
              >
                {employee?.name}
              </button>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Клиент:</p>
              <p className="font-medium">{client?.name}</p>
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
              <Badge className={getSentimentColor(call.sentiment)}>
                {getSentimentLabel(call.sentiment)}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-neutral-500">Соблюдение скрипта:</p>
              <p className="font-medium">{call.scriptCompliance}%</p>
            </div>
          </div>
          
          {/* Ссылка на аудио */}
          <div className="flex items-center gap-2 p-3 border rounded-lg">
            <Play className="w-5 h-5 text-neutral-500" />
            <a href={call.audioUrl} className="text-blue-600 hover:underline">
              {call.audioUrl}
            </a>
          </div>
          
          {/* Текст диалога */}
          <div>
            <p className="text-sm text-neutral-500 mb-2">Текст диалога:</p>
            <ScrollArea className="h-[300px] border rounded-lg p-4">
              <div className="space-y-3">
                {call.transcript.map((message, index) => (
                  <div 
                    key={index}
                    className={`p-3 rounded-lg ${
                      message.speaker === 'operator' 
                        ? 'bg-blue-50 ml-0 mr-8' 
                        : 'bg-neutral-100 ml-8 mr-0'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-medium text-neutral-500">
                        {message.speaker === 'operator' ? 'Оператор' : 'Клиент'}
                      </span>
                      <span className="text-xs text-neutral-400">{message.timestamp}</span>
                    </div>
                    <p className="text-sm">{message.text}</p>
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
