import AsyncStorage from '@react-native-async-storage/async-storage';
import { ConsultaLegal, RespuestaLegal, DocumentoLegal } from './apiservice';

// Interfaz para las consultas almacenadas localmente
export interface ConsultaAlmacenada {
  id: string;
  pregunta: string;
  respuesta: string;
  fecha: string;
  tipo_lenguaje: 'tecnico' | 'coloquial' | 'mixto';
  confianza: number;
  tiempo_procesamiento: number;
  fundamentos_legales?: DocumentoLegal[];
  advertencias?: string[];
  sugerencias?: string[];
  sincronizado: boolean; // Para saber si ya se envió al servidor
}

const STORAGE_KEY = 'lexia_consultas_historial';

class StorageService {
  // Guardar una nueva consulta
  async guardarConsulta(
    consulta: ConsultaLegal, 
    respuesta: RespuestaLegal
  ): Promise<void> {
    try {
      const consultaAlmacenada: ConsultaAlmacenada = {
        id: Date.now().toString(),
        pregunta: consulta.pregunta,
        respuesta: respuesta.respuesta,
        fecha: new Date().toISOString(),
        tipo_lenguaje: respuesta.tipo_lenguaje_usado,
        confianza: respuesta.confianza,
        tiempo_procesamiento: respuesta.tiempo_procesamiento,
        fundamentos_legales: respuesta.fundamentos_legales,
        advertencias: respuesta.advertencias,
        sugerencias: respuesta.sugerencias,
        sincronizado: false
      };

      const consultasExistentes = await this.obtenerConsultas();
      const nuevasConsultas = [consultaAlmacenada, ...consultasExistentes];
      
      // Mantener solo las últimas 100 consultas para no saturar el almacenamiento
      const consultasLimitadas = nuevasConsultas.slice(0, 100);
      
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(consultasLimitadas));
    } catch (error) {
      console.error('Error al guardar consulta:', error);
    }
  }

  // Obtener todas las consultas almacenadas
  async obtenerConsultas(): Promise<ConsultaAlmacenada[]> {
    try {
      const consultasJson = await AsyncStorage.getItem(STORAGE_KEY);
      if (consultasJson) {
        return JSON.parse(consultasJson);
      }
      return [];
    } catch (error) {
      console.error('Error al obtener consultas:', error);
      return [];
    }
  }

  // Limpiar todo el historial
  async limpiarHistorial(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Error al limpiar historial:', error);
    }
  }

  // Marcar consultas como sincronizadas
  async marcarComoSincronizadas(ids: string[]): Promise<void> {
    try {
      const consultas = await this.obtenerConsultas();
      const consultasActualizadas = consultas.map(consulta => {
        if (ids.includes(consulta.id)) {
          return { ...consulta, sincronizado: true };
        }
        return consulta;
      });
      
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(consultasActualizadas));
    } catch (error) {
      console.error('Error al marcar como sincronizadas:', error);
    }
  }

  // Obtener consultas no sincronizadas
  async obtenerConsultasNoSincronizadas(): Promise<ConsultaAlmacenada[]> {
    try {
      const consultas = await this.obtenerConsultas();
      return consultas.filter(consulta => !consulta.sincronizado);
    } catch (error) {
      console.error('Error al obtener consultas no sincronizadas:', error);
      return [];
    }
  }
}

export const storageService = new StorageService();
export default storageService;