import type { ApiConfig, ApiProvider, Provider } from "./types";

export const API_CONFIG_STORAGE_KEY = "crh-create-ai:api-config";

export const defaultBaseUrlByProvider: Record<Provider, string> = {
  auto: "https://api.openai.com/v1",
  openai: "https://api.openai.com/v1",
  gemini: "https://generativelanguage.googleapis.com/v1beta",
  deepseek: "https://api.deepseek.com",
  custom: ""
};

export const defaultModelByProvider: Record<Provider, string> = {
  auto: "gpt-5.5",
  openai: "gpt-5.5",
  gemini: "gemini-2.5-pro",
  deepseek: "deepseek-v3",
  custom: "custom-model"
};

export function createDefaultApiConfig(provider: ApiProvider = "openai"): ApiConfig {
  return {
    provider,
    apiKey: "",
    baseUrl: defaultBaseUrlByProvider[provider],
    model: defaultModelByProvider[provider]
  };
}

export function loadApiConfig(): ApiConfig | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(API_CONFIG_STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<ApiConfig>;
    if (!parsed.provider || !parsed.apiKey) return null;
    return {
      provider: parsed.provider,
      apiKey: parsed.apiKey,
      baseUrl: parsed.baseUrl || defaultBaseUrlByProvider[parsed.provider],
      model: parsed.model || defaultModelByProvider[parsed.provider]
    };
  } catch {
    return null;
  }
}

export function saveApiConfig(config: ApiConfig) {
  window.localStorage.setItem(API_CONFIG_STORAGE_KEY, JSON.stringify(config));
}

export function clearApiConfig() {
  window.localStorage.removeItem(API_CONFIG_STORAGE_KEY);
}
