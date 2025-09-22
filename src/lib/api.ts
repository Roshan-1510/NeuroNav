// API client for NeuroNav backend communication
// Updated to match actual backend routes as of Sept 20, 2025
import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000';

// Types for API responses
export interface User {
  id: string;
  name: string;
  email: string;
  brain_type?: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
  message: string;
}

export interface QuizQuestion {
  question_id: string;
  question_number: number;
  text: string;
  options: {
    option_id: number;
    text: string;
  }[];
}

export interface QuizResponse {
  message: string;
  assessment_results: {
    brain_type: string;
    confidence_score: number;
    brain_type_distribution: Record<string, number>;
    total_questions_answered: number;
  };
  brain_type_description: {
    description: string;
    learning_tips: string[];
    strengths: string[];
  };
  roadmap: {
    roadmap_id: string;
    topic: string;
    estimated_completion_weeks: number;
    daily_time_minutes: number;
    total_steps: number;
  };
  next_steps: string[];
}

export interface RoadmapStep {
  step_number: number;
  title: string;
  description: string;
  resource_id: string;
  resource_url: string;
  resource_type: string;
  estimated_time_minutes: number;
  tags: string[];
  brain_type_optimized: boolean;
  completed?: boolean;
  completed_at?: string;
}

export interface Roadmap {
  roadmap_id: string;
  user_id: string;
  topic: string;
  brain_type: string;
  steps: RoadmapStep[];
  estimated_completion_weeks: number;
  daily_time_minutes: number;
  created_at: string;
  updated_at?: string;
  progress_summary?: {
    total_steps: number;
    completed_steps: number;
    completion_percentage: number;
  };
}

export interface ProgressSummary {
  roadmap_id: string;
  roadmap_title: string;
  brain_type: string;
  total_steps: number;
  completed_steps: number;
  completion_percentage: number;
  last_activity: string;
  created_at: string;
}

// Token management
export const getToken = (): string | null => {
  return localStorage.getItem('neuronav_token');
};

export const setToken = (token: string): void => {
  localStorage.setItem('neuronav_token', token);
};

export const removeToken = (): void => {
  localStorage.removeItem('neuronav_token');
};

export const getAuthHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// API error handling
class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new ApiError(response.status, errorData.error || 'Request failed');
  }
  return response.json();
};

// Authentication APIs
export const authApi = {
  register: async (name: string, email: string, password: string): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    return handleResponse(response);
  },

  login: async (email: string, password: string): Promise<{ access_token: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },

  verifyToken: async (): Promise<{ msg: string; user: { id: string; name: string; email: string } }> => {
    const response = await fetch(`${API_BASE_URL}/auth/verify-token`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
};

// Quiz APIs
export const quizApi = {
  getQuestions: async (): Promise<{ questions: QuizQuestion[]; total_questions: number; instructions: string }> => {
    const response = await fetch(`${API_BASE_URL}/quiz/questions`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  submitQuiz: async (answers: { question_id: string; selected_option: number }[], preferences: { topic?: string; duration?: string; intensity?: string } = {}): Promise<QuizResponse> => {
    const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ answers, preferences }),
    });
    return handleResponse(response);
  },
};

// Progress APIs
export const progressApi = {
  updateStepProgress: async (roadmapId: string, stepNumber: number, completed: boolean): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}/progress`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ step_number: stepNumber, completed }),
    });
    return handleResponse(response);
  },

  getRoadmapProgress: async (roadmapId: string): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}/progress`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  getUserProgressSummary: async (): Promise<{
    user_id: string;
    roadmaps: ProgressSummary[];
    overall_summary: {
      total_roadmaps: number;
      total_steps: number;
      completed_steps: number;
      overall_completion_percentage: number;
    };
  }> => {
    const response = await fetch(`${API_BASE_URL}/progress/summary`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
};

// Roadmap APIs
export const roadmapApi = {
  getRoadmap: async (roadmapId: string): Promise<Roadmap> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  deleteRoadmap: async (roadmapId: string): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  getUserRoadmaps: async (): Promise<{ roadmaps: Roadmap[]; total_roadmaps: number }> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  updateRoadmap: async (roadmapId: string, updateData: Partial<Roadmap>): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(updateData),
    });
    return handleResponse(response);
  },

  addStep: async (roadmapId: string, stepData: Partial<RoadmapStep> & { insert_position?: number }): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}/steps`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(stepData),
    });
    return handleResponse(response);
  },

  deleteStep: async (roadmapId: string, stepNumber: number): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}/steps/${stepNumber}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  reorderSteps: async (roadmapId: string, stepOrder: number[]): Promise<unknown> => {
    const response = await fetch(`${API_BASE_URL}/roadmaps/${roadmapId}/steps/reorder`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ step_order: stepOrder }),
    });
    return handleResponse(response);
  },
};

// Admin APIs (for future use)
export const adminApi = {
  getResources: async (filters: { topic?: string; type?: string } = {}): Promise<unknown> => {
    const params = new URLSearchParams();
    if (filters.topic) params.append('topic', filters.topic);
    if (filters.type) params.append('type', filters.type);
    
    const response = await fetch(`${API_BASE_URL}/admin/resources?${params}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
};

// User context hook
export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (token) {
      authApi.verifyToken()
        .then(({ user }) => setUser(user))
        .catch(() => removeToken())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const { access_token } = await authApi.login(email, password);
    setToken(access_token);
    // Get user info after login
    const { user } = await authApi.verifyToken();
    setUser(user);
    return user;
  };

  const register = async (name: string, email: string, password: string) => {
    await authApi.register(name, email, password);
    // After registration, login to get token and user data
    return await login(email, password);
  };

  const logout = () => {
    removeToken();
    setUser(null);
  };

  return { user, loading, login, register, logout };
};