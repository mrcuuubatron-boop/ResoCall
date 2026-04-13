// Mock данные сотрудников
export interface Employee {
  id: string
  name: string
  position: string
  hireDate: string
}

export const employees: Employee[] = [
  { id: "emp1", name: "Иванова Анна Сергеевна", position: "Старший оператор", hireDate: "2024-01-15" },
  { id: "emp2", name: "Петров Дмитрий Александрович", position: "Оператор", hireDate: "2024-03-20" },
  { id: "emp3", name: "Сидорова Мария Ивановна", position: "Оператор", hireDate: "2024-02-10" },
  { id: "emp4", name: "Козлов Алексей Николаевич", position: "Оператор", hireDate: "2024-05-05" },
  { id: "emp5", name: "Новикова Елена Петровна", position: "Старший оператор", hireDate: "2023-11-01" },
  { id: "emp6", name: "Морозов Сергей Викторович", position: "Оператор", hireDate: "2024-06-15" },
]

// Mock данные клиентов
export interface Client {
  id: string
  name: string
  phone: string
}

export const clients: Client[] = [
  { id: "cl1", name: "Кузнецов Иван Петрович", phone: "+7 (900) 123-45-67" },
  { id: "cl2", name: "Смирнова Ольга Александровна", phone: "+7 (901) 234-56-78" },
  { id: "cl3", name: "Федоров Андрей Михайлович", phone: "+7 (902) 345-67-89" },
  { id: "cl4", name: "Волкова Наталья Сергеевна", phone: "+7 (903) 456-78-90" },
  { id: "cl5", name: "Соколов Михаил Иванович", phone: "+7 (904) 567-89-01" },
  { id: "cl6", name: "Попова Екатерина Дмитриевна", phone: "+7 (905) 678-90-12" },
  { id: "cl7", name: "Лебедев Артем Олегович", phone: "+7 (906) 789-01-23" },
  { id: "cl8", name: "Козлова Анна Викторовна", phone: "+7 (907) 890-12-34" },
]

// Тип настроения
export type Sentiment = "positive" | "neutral" | "negative"

// Mock данные звонков
export interface Call {
  id: string
  employeeId: string
  clientId: string
  date: string // ISO формат даты
  duration: number // в секундах
  sentiment: Sentiment
  scriptCompliance: number // 0-100
  category: string
  isProcessed: boolean
  errorReason?: string
  audioUrl: string
  transcript: DialogMessage[]
}

export interface DialogMessage {
  speaker: "operator" | "client"
  text: string
  timestamp: string
}

// Генерация mock диалогов
const dialogTemplates: DialogMessage[][] = [
  [
    { speaker: "operator", text: "Добрый день! Компания 'Неосистемы', меня зовут Анна. Чем могу вам помочь?", timestamp: "00:00" },
    { speaker: "client", text: "Здравствуйте! У меня проблема с оплатой услуг.", timestamp: "00:05" },
    { speaker: "operator", text: "Понимаю вас. Позвольте уточнить номер вашего договора?", timestamp: "00:12" },
    { speaker: "client", text: "Да, конечно. Договор номер 12345.", timestamp: "00:18" },
    { speaker: "operator", text: "Спасибо. Вижу ваш договор. Какая именно проблема с оплатой?", timestamp: "00:25" },
    { speaker: "client", text: "Платеж не прошел, хотя деньги списались с карты.", timestamp: "00:32" },
    { speaker: "operator", text: "Сейчас проверю информацию. Одну минуту, пожалуйста.", timestamp: "00:40" },
    { speaker: "operator", text: "Да, вижу. Платеж находится в обработке. Он будет зачислен в течение 24 часов.", timestamp: "01:15" },
    { speaker: "client", text: "Хорошо, спасибо за информацию!", timestamp: "01:25" },
    { speaker: "operator", text: "Пожалуйста! Есть ли у вас еще вопросы?", timestamp: "01:30" },
    { speaker: "client", text: "Нет, это все. До свидания!", timestamp: "01:35" },
    { speaker: "operator", text: "Спасибо за обращение! Хорошего дня!", timestamp: "01:40" },
  ],
  [
    { speaker: "operator", text: "Добрый день! Компания 'Неосистемы', Дмитрий. Слушаю вас.", timestamp: "00:00" },
    { speaker: "client", text: "Алло, здравствуйте. Хочу узнать про тарифы.", timestamp: "00:04" },
    { speaker: "operator", text: "Конечно! Какой тариф вас интересует - базовый или расширенный?", timestamp: "00:10" },
    { speaker: "client", text: "Расскажите про оба, пожалуйста.", timestamp: "00:16" },
    { speaker: "operator", text: "Базовый тариф включает 100 минут и 5 ГБ интернета за 500 рублей в месяц.", timestamp: "00:22" },
    { speaker: "operator", text: "Расширенный - безлимитные звонки и 30 ГБ за 900 рублей.", timestamp: "00:35" },
    { speaker: "client", text: "А можно подключить расширенный прямо сейчас?", timestamp: "00:45" },
    { speaker: "operator", text: "Да, конечно. Давайте оформим заявку. Ваш номер телефона?", timestamp: "00:52" },
    { speaker: "client", text: "901-234-56-78", timestamp: "01:00" },
    { speaker: "operator", text: "Отлично, заявка оформлена. Тариф будет активирован в течение часа.", timestamp: "01:10" },
    { speaker: "client", text: "Супер, спасибо большое!", timestamp: "01:18" },
    { speaker: "operator", text: "Рады помочь! До свидания!", timestamp: "01:22" },
  ],
  [
    { speaker: "operator", text: "Здравствуйте, компания 'Неосистемы'. Мария на связи.", timestamp: "00:00" },
    { speaker: "client", text: "Да, здравствуйте. Я уже третий раз звоню! Когда решите мою проблему?!", timestamp: "00:05" },
    { speaker: "operator", text: "Прошу прощения за неудобства. Позвольте узнать суть проблемы?", timestamp: "00:12" },
    { speaker: "client", text: "Интернет не работает уже неделю! Это безобразие!", timestamp: "00:18" },
    { speaker: "operator", text: "Понимаю ваше недовольство. Сейчас проверю статус заявки.", timestamp: "00:25" },
    { speaker: "operator", text: "Вижу заявку. К сожалению, произошла задержка из-за технических работ в вашем районе.", timestamp: "00:45" },
    { speaker: "client", text: "И сколько еще ждать?", timestamp: "00:52" },
    { speaker: "operator", text: "Работы будут завершены завтра до 18:00. Приносим извинения.", timestamp: "01:00" },
    { speaker: "client", text: "Ладно, буду ждать. Но если опять не заработает - расторгну договор!", timestamp: "01:10" },
    { speaker: "operator", text: "Понимаю. Мы сделаем все возможное. Могу ли я чем-то еще помочь?", timestamp: "01:20" },
    { speaker: "client", text: "Нет. До свидания.", timestamp: "01:28" },
    { speaker: "operator", text: "Всего доброго!", timestamp: "01:32" },
  ],
  [
    { speaker: "operator", text: "Добрый день! Неосистемы, Алексей. Чем могу помочь?", timestamp: "00:00" },
    { speaker: "client", text: "Привет! Хотел уточнить баланс на счете.", timestamp: "00:05" },
    { speaker: "operator", text: "Конечно. Назовите, пожалуйста, номер договора.", timestamp: "00:10" },
    { speaker: "client", text: "54321", timestamp: "00:15" },
    { speaker: "operator", text: "Ваш текущий баланс составляет 1250 рублей.", timestamp: "00:22" },
    { speaker: "client", text: "Отлично, спасибо!", timestamp: "00:27" },
    { speaker: "operator", text: "Пожалуйста! Что-нибудь еще?", timestamp: "00:30" },
    { speaker: "client", text: "Нет, все. Пока!", timestamp: "00:34" },
    { speaker: "operator", text: "До свидания!", timestamp: "00:37" },
  ],
  [
    { speaker: "operator", text: "Добрый день! Компания 'Неосистемы', Елена. Слушаю вас.", timestamp: "00:00" },
    { speaker: "client", text: "Здравствуйте! Хочу подключить дополнительную услугу.", timestamp: "00:06" },
    { speaker: "operator", text: "С удовольствием помогу! Какая услуга вас интересует?", timestamp: "00:12" },
    { speaker: "client", text: "Облачное хранилище для бизнеса.", timestamp: "00:18" },
    { speaker: "operator", text: "Отличный выбор! У нас есть тарифы на 100 ГБ, 500 ГБ и 1 ТБ.", timestamp: "00:24" },
    { speaker: "client", text: "Расскажите подробнее про 500 ГБ.", timestamp: "00:32" },
    { speaker: "operator", text: "Тариф 500 ГБ стоит 1500 рублей в месяц, включает резервное копирование и доступ для 10 пользователей.", timestamp: "00:40" },
    { speaker: "client", text: "Звучит хорошо. Можно подключить?", timestamp: "00:52" },
    { speaker: "operator", text: "Конечно! Для оформления мне понадобятся ваши данные. Номер договора?", timestamp: "01:00" },
    { speaker: "client", text: "67890", timestamp: "01:08" },
    { speaker: "operator", text: "Спасибо. Услуга будет активирована в течение 2 часов. На почту придет инструкция.", timestamp: "01:20" },
    { speaker: "client", text: "Замечательно! Большое спасибо за помощь!", timestamp: "01:30" },
    { speaker: "operator", text: "Всегда рады помочь! Хорошего дня!", timestamp: "01:36" },
  ],
]

// Генерация звонков за последние 30 дней
function generateCalls(): Call[] {
  const calls: Call[] = []
  const categories = ["Оплата", "Тарифы", "Техническая поддержка", "Консультация", "Подключение услуг", "Жалоба"]
  const sentiments: Sentiment[] = ["positive", "neutral", "negative"]
  
  const now = new Date()
  
  for (let i = 0; i < 150; i++) {
    const daysAgo = Math.floor(Math.random() * 30)
    const hoursAgo = Math.floor(Math.random() * 24)
    const minutesAgo = Math.floor(Math.random() * 60)
    
    const callDate = new Date(now)
    callDate.setDate(callDate.getDate() - daysAgo)
    callDate.setHours(9 + Math.floor(Math.random() * 10), minutesAgo, 0, 0)
    
    const employeeIndex = Math.floor(Math.random() * employees.length)
    const clientIndex = Math.floor(Math.random() * clients.length)
    const dialogIndex = Math.floor(Math.random() * dialogTemplates.length)
    
    const isProcessed = Math.random() > 0.05 // 95% обработаны
    const sentiment = sentiments[Math.floor(Math.random() * sentiments.length)]
    const scriptCompliance = isProcessed ? 60 + Math.floor(Math.random() * 40) : 0
    
    const errorReasons = [
      "Низкое качество аудио",
      "Timeout обработки",
      "Ошибка распознавания речи",
      "Слишком короткий звонок",
      "Технический сбой"
    ]
    
    calls.push({
      id: `call-${i + 1}`,
      employeeId: employees[employeeIndex].id,
      clientId: clients[clientIndex].id,
      date: callDate.toISOString(),
      duration: 60 + Math.floor(Math.random() * 600), // от 1 до 11 минут
      sentiment: isProcessed ? sentiment : "neutral",
      scriptCompliance,
      category: categories[Math.floor(Math.random() * categories.length)],
      isProcessed,
      errorReason: isProcessed ? undefined : errorReasons[Math.floor(Math.random() * errorReasons.length)],
      audioUrl: `/audio/call-${i + 1}.mp3`,
      transcript: dialogTemplates[dialogIndex],
    })
  }
  
  // Сортировка по дате (новые первые)
  return calls.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export const calls: Call[] = generateCalls()

// Вспомогательные функции
export function getEmployeeById(id: string): Employee | undefined {
  return employees.find(emp => emp.id === id)
}

export function getClientById(id: string): Client | undefined {
  return clients.find(cl => cl.id === id)
}

export function getCallsByEmployeeId(employeeId: string): Call[] {
  return calls.filter(call => call.employeeId === employeeId)
}

export function getCallsByDateRange(startDate: Date, endDate: Date): Call[] {
  return calls.filter(call => {
    const callDate = new Date(call.date)
    return callDate >= startDate && callDate <= endDate
  })
}

export function getProcessedCalls(): Call[] {
  return calls.filter(call => call.isProcessed)
}

export function getUnprocessedCalls(): Call[] {
  return calls.filter(call => !call.isProcessed)
}

// Функция расчета рейтинга сотрудника
export function calculateEmployeeRating(employeeId: string, startDate?: Date, endDate?: Date): {
  rating: number
  callsCount: number
  avgScriptCompliance: number
  avgSentiment: number
  sentimentScore: number
} {
  let employeeCalls = getCallsByEmployeeId(employeeId).filter(c => c.isProcessed)
  
  if (startDate && endDate) {
    employeeCalls = employeeCalls.filter(call => {
      const callDate = new Date(call.date)
      return callDate >= startDate && callDate <= endDate
    })
  }
  
  if (employeeCalls.length === 0) {
    return { rating: 0, callsCount: 0, avgScriptCompliance: 0, avgSentiment: 0, sentimentScore: 0 }
  }
  
  const avgScriptCompliance = employeeCalls.reduce((acc, call) => acc + call.scriptCompliance, 0) / employeeCalls.length
  
  // Расчет среднего настроения (positive=100, neutral=50, negative=0)
  const sentimentValues = { positive: 100, neutral: 50, negative: 0 }
  const avgSentiment = employeeCalls.reduce((acc, call) => acc + sentimentValues[call.sentiment], 0) / employeeCalls.length
  
  // Формула рейтинга: 60% соблюдение скрипта + 40% тональность, масштаб 0-5
  const rating = ((avgScriptCompliance * 0.6) + (avgSentiment * 0.4)) / 20
  
  return {
    rating: Math.round(rating * 10) / 10,
    callsCount: employeeCalls.length,
    avgScriptCompliance: Math.round(avgScriptCompliance),
    avgSentiment: Math.round(avgSentiment),
    sentimentScore: avgSentiment
  }
}

// Форматирование длительности
export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// Форматирование даты
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Получение названия настроения на русском
export function getSentimentLabel(sentiment: Sentiment): string {
  const labels = {
    positive: "Позитивный",
    neutral: "Нейтральный",
    negative: "Негативный"
  }
  return labels[sentiment]
}

// Получение цвета настроения
export function getSentimentColor(sentiment: Sentiment): string {
  const colors = {
    positive: "text-green-600 bg-green-50",
    neutral: "text-neutral-600 bg-neutral-100",
    negative: "text-red-600 bg-red-50"
  }
  return colors[sentiment]
}
