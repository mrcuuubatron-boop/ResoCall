export interface ModuleSettingsResponse {
  module_key: string
  settings: Record<string, unknown>
  updated_at: string | null
}

function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL
  if (configured) return configured

  // Build backend URL from current browser host by default.
  if (typeof window !== "undefined") {
    const protocol = window.location.protocol || "http:"
    const host = window.location.hostname || "localhost"
    const port = process.env.NEXT_PUBLIC_API_PORT || "8000"
    return `${protocol}//${host}:${port}`
  }

  return "http://localhost:8000"
}

function buildAuthHeaders(login: string, password: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    "x-login": login,
    "x-password": password,
  }
}

export async function loadModuleSettings(
  moduleKey: string,
  login: string,
  password: string,
): Promise<ModuleSettingsResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/modules/${moduleKey}/settings`, {
    method: "GET",
    headers: buildAuthHeaders(login, password),
  })

  if (!response.ok) {
    throw new Error("Не удалось загрузить настройки модуля")
  }

  return (await response.json()) as ModuleSettingsResponse
}

export async function saveModuleSettings(
  moduleKey: string,
  settings: Record<string, unknown>,
  login: string,
  password: string,
): Promise<ModuleSettingsResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/modules/${moduleKey}/settings`, {
    method: "PUT",
    headers: buildAuthHeaders(login, password),
    body: JSON.stringify({ settings }),
  })

  if (!response.ok) {
    throw new Error("Не удалось сохранить настройки модуля")
  }

  return (await response.json()) as ModuleSettingsResponse
}
