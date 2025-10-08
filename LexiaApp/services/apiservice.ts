import axios from 'axios';

// Configuración de la API
// Para desarrollo móvil, usar la IP de la red local en lugar de localhost
const API_BASE_URL = 'http://192.168.1.108:8000'; // IP de la red local para acceso desde smartphones

// Tipos para la API Legal
export interface ConsultaLegal {
  pregunta: string;
  contexto_adicional?: string;
  tipo_lenguaje?: 'tecnico' | 'coloquial' | 'mixto';
  incluir_fundamentos?: boolean;
  max_documentos?: number;
  umbral_relevancia?: number;
  incluir_metadatos?: boolean;
}

export interface DocumentoLegal {
  id: string;
  titulo: string;
  tipo: string;
  fuente: string;
  url?: string;
  relevancia: number;
  fragmento: string;
  articulo?: string;
  fecha_publicacion?: string;
}

export interface RespuestaLegal {
  respuesta: string;
  tipo_lenguaje_usado: 'tecnico' | 'coloquial' | 'mixto';
  fundamentos_legales: DocumentoLegal[];
  confianza: number;
  advertencias: string[];
  sugerencias: string[];
  tiempo_procesamiento: number;
  timestamp: string;
}

export interface EstadisticasAPI {
  total_consultas: number;
  consultas_hoy: number;
  tiempo_promedio_respuesta: number;
  tipos_consulta_frecuentes: string[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class ApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 100000, // 30 segundos
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para manejo de errores
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Error en API:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Realiza una consulta legal
   */
  async realizarConsulta(consulta: ConsultaLegal): Promise<ApiResponse<RespuestaLegal>> {
    try {
      const response = await this.axiosInstance.post<RespuestaLegal>('/legal/consulta', consulta);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Error desconocido',
      };
    }
  }

  /**
   * Obtiene estadísticas de la API
   */
  async obtenerEstadisticas(): Promise<ApiResponse<EstadisticasAPI>> {
    try {
      const response = await this.axiosInstance.get<EstadisticasAPI>('/admin/estadisticas');
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Error desconocido',
      };
    }
  }

  /**
   * Verifica el estado de salud de la API
   */
  async verificarSalud(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    try {
      const response = await this.axiosInstance.get('/admin/salud');
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Error desconocido',
      };
    }
  }

  /**
   * Obtiene el historial de consultas (si está disponible)
   */
  async obtenerHistorial(): Promise<ApiResponse<RespuestaLegal[]>> {
    try {
      const response = await this.axiosInstance.get<RespuestaLegal[]>('/admin/historial');
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Error desconocido',
      };
    }
  }
}

export const apiService = new ApiService();
export default apiService;