import axios, {
  AxiosError,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set(access: string, refresh?: string) {
    localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export const api = axios.create({ baseURL: BASE_URL });

// Attach the access token to every request.
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, try to refresh the access token once, then replay the request.
let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStore.refresh;
  if (!refresh) throw new Error("no refresh token");
  const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, { refresh });
  tokenStore.set(data.access, data.refresh);
  return data.access;
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry && tokenStore.refresh) {
      original._retry = true;
      try {
        refreshing = refreshing ?? refreshAccessToken();
        const access = await refreshing;
        refreshing = null;
        original.headers = { ...original.headers, Authorization: `Bearer ${access}` };
        return api(original);
      } catch {
        refreshing = null;
        tokenStore.clear();
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  },
);
