# ResoCall — Анализ деятельности операторов call-центра с помощью ИИ

Веб-приложение для интеллектуального анализа работы операторов call-центра с использованием технологий машинного обучения.

## Описание проекта

Система предназначена для:
- Автоматического распознавания голосовых сообщений
- Детекции эмоционального состояния звонящего
- Классификации типов проблем клиентов
- Контроля соблюдения скриптов звонков
- Анализа качества работы операторов

## Роли пользователей

| Роль | Логин | Пароль | Описание |
|------|-------|--------|----------|
| Пользователь (работник) | user | user | Оператор call-центра, работает с архивом своих диалогов |
| Инженер отдела качества | engineer | engineer | Контролирует качество работы операторов, анализирует статистику |
| Администратор | admin | admin | Управляет работой нейросети, просматривает логи |

---

## Установка и запуск

### Требования

- Node.js версии 18 или выше
- npm или pnpm (менеджер пакетов)

---

## Windows 10/11

### 1. Установка Node.js

1. Перейдите на сайт [https://nodejs.org/](https://nodejs.org/)
2. Скачайте LTS версию (рекомендуется)
3. Запустите установщик и следуйте инструкциям
4. После установки откройте командную строку (cmd) или PowerShell и проверьте:

```cmd
node --version
npm --version
```

### 2. Установка pnpm (опционально, но рекомендуется)

```cmd
npm install -g pnpm
```

### 3. Скачивание проекта

Скачайте ZIP-архив проекта и распакуйте его в удобную папку, например `C:\Projects\resocall`

### 4. Установка зависимостей

Откройте командную строку в папке проекта:

```cmd
cd C:\Projects\resocall
pnpm install
```

Или с использованием npm:

```cmd
npm install
```

### 5. Запуск проекта

```cmd
pnpm dev
```

Или:

```cmd
npm run dev
```

### 6. Открытие в браузере

Откройте браузер и перейдите по адресу:

```
http://localhost:3000
```

Если порт 3000 занят, запустите на другом порту:

```cmd
pnpm dev --port 3001
```

---

## Linux (Debian/Ubuntu)

### 1. Установка Node.js

**Вариант А: Через NodeSource (рекомендуется)**

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Вариант Б: Через apt (может быть устаревшая версия)**

```bash
sudo apt update
sudo apt install nodejs npm
```

Проверьте установку:

```bash
node --version
npm --version
```

### 2. Установка pnpm

```bash
sudo npm install -g pnpm
```

### 3. Скачивание и распаковка проекта

```bash
cd ~/Загрузки
unzip resocall.zip
cd resocall
```

### 4. Установка зависимостей

```bash
pnpm install
```

Или:

```bash
npm install
```

### 5. Запуск проекта

```bash
pnpm dev
```

Или:

```bash
npm run dev
```

### 6. Открытие в браузере

```
http://localhost:3000
```

Если порт занят:

```bash
pnpm dev --port 3001
```

---

## Возможные проблемы и решения

### Ошибка "command not found: pnpm"

Установите pnpm:

```bash
sudo npm install -g pnpm
```

### Ошибка "next: not found"

Не установлены зависимости. Выполните:

```bash
pnpm install
```

### Порт 3000 занят

Запустите на другом порту:

```bash
pnpm dev --port 3001
```

### Ошибка прав доступа при установке глобальных пакетов (Linux)

Используйте sudo:

```bash
sudo npm install -g pnpm
```

---

## Сборка для продакшена

```bash
pnpm build
pnpm start
```

---

## Структура проекта

```
resocall/
├── app/
│   ├── page.tsx          # Главная страница
│   ├── layout.tsx        # Основной layout
│   └── globals.css       # Глобальные стили
├── components/
│   ├── auth-panel.tsx    # Панель авторизации
│   ├── user-panel.tsx    # Панель пользователя (работника)
│   ├── engineer-panel.tsx # Панель инженера отдела качества
│   └── admin-panel.tsx   # Панель администратора
├── package.json
└── README.md
```

---

## Рекомендуемые редакторы кода

- **Visual Studio Code** — [https://code.visualstudio.com/](https://code.visualstudio.com/)
- **WebStorm** — [https://www.jetbrains.com/webstorm/](https://www.jetbrains.com/webstorm/)

Рекомендуемые расширения для VS Code:
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Prettier
- ESLint

---

## Контакты

**Заказчик:** Дибров Иван Васильевич  
**Должность:** Руководитель отделения внедрения ООО "Неосистемы ИТ"  
**Email:** i.dibrov@neosystems.ru

---

**Проект "ResoCall" — ООО "Неосистемы ИТ"**
