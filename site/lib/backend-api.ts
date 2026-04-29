export interface BackendHealthResponse {
  status: string
  workers: number
  db_backend: string
  database_ok: boolean
  asr_model: string
  external_asr_enabled: boolean
  external_asr_status: string
  external_asr_module_path: string
  external_asr_error: string | null
}

export interface LoginResponse {
  ok: boolean
  role: "admin" | "engineer" | "user"
  token: string
}

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
}

export function getApiUrl(path: string): string {
  return `${getApiBaseUrl()}${path}`
}

export async function fetchBackendHealth(): Promise<BackendHealthResponse> {
  const response = await fetch(getApiUrl("/api/v1/health"), {
    cache: "no-store",
  })

  if (!response.ok) {
    throw new Error("Не удалось получить статус backend")
  }

  return (await response.json()) as BackendHealthResponse
}

export async function loginWithBackend(login: string, password: string): Promise<LoginResponse> {
  const response = await fetch(getApiUrl("/api/v1/auth/login"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ login, password }),
  })

  if (!response.ok) {
    throw new Error("Неверный логин или пароль")
  }

  return (await response.json()) as LoginResponse
}