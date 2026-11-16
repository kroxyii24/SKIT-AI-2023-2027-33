import axios, {
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// Attach the access token to authenticated requests.
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  }
);

// Centralized API error handling.
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (!error.response) {
      return Promise.reject(
        new Error("Unable to connect to the server. Please try again.")
      );
    }

    if (error.response.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }

    return Promise.reject(error);
  }
);

export interface ChatSource {
  publisher: string;
  source_url: string | null;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: ChatSource[];
  confidence: number | null;
  is_emergency: boolean;
}

export async function sendChatMessage(
  message: string,
  sessionId: string | null,
  language: string = "en"
): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>("/chat/message", {
    message,
    session_id: sessionId,
    language,
  });

  return data;
}

export async function login(phoneNumber: string, password: string) {
  const { data } = await apiClient.post("/auth/login", {
    phone_number: phoneNumber,
    password,
  });

  return data;
}

export async function requestRegistrationOTP(
  fullName: string,
  phoneNumber: string,
  email: string,
  password: string,
  language: string
) {
  const { data } = await apiClient.post("/auth/register/request-otp", {
    full_name: fullName,
    phone_number: phoneNumber,
    email,
    password,
    preferred_language: language,
  });

  return data;
}

export async function verifyRegistrationOTP(email: string, otp: string) {
  const { data } = await apiClient.post("/auth/register/verify-otp", {
    email,
    otp,
  });

  return data;
}

export async function resendRegistrationOTP(email: string) {
  const { data } = await apiClient.post("/auth/register/resend-otp", {
    email,
  });

  return data;
}
