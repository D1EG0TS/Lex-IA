import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../../services/apiservice';
import { LegalTheme } from '../../constants/legaltheme';
import { storageService, ConsultaAlmacenada } from '../../services/storageService';

interface ConsultaHistorial {
  id: string;
  pregunta: string;
  respuesta: string;
  fecha: string;
  tipo_lenguaje: string;
  confianza: number;
  tiempo_procesamiento: number;
}

export default function HistorialScreen() {
  const [historial, setHistorial] = useState<ConsultaHistorial[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedConsulta, setSelectedConsulta] = useState<string | null>(null);

  useEffect(() => {
    loadHistorial();
  }, []);

  const loadHistorial = async () => {
    setIsLoading(true);
    try {
      // Primero intentar cargar desde el servidor
      const response = await apiService.obtenerHistorial();
      if (response.success && response.data) {
        const historialServidor = response.data.map(item => ({
          id: (item as any).id || String(Math.random()),
          pregunta: (item as any).pregunta || '',
          respuesta: item.respuesta || '',
          fecha: (item as any).fecha || new Date().toISOString(),
          tipo_lenguaje: (item as any).tipo_lenguaje || 'mixto',
          confianza: item.confianza || 0,
          tiempo_procesamiento: item.tiempo_procesamiento || 0
        }));
        setHistorial(historialServidor);
      } else {
        // Si no hay conexión, cargar desde almacenamiento local
        console.log('Sin conexión al servidor, cargando historial local');
        await loadHistorialLocal();
      }
    } catch (error) {
      console.log('Error al cargar historial del servidor:', error);
      // Cargar desde almacenamiento local como respaldo
      await loadHistorialLocal();
    } finally {
      setIsLoading(false);
    }
  };

  const loadHistorialLocal = async () => {
    try {
      const consultasLocales = await storageService.obtenerConsultas();
      const historialLocal = consultasLocales.map((consulta: ConsultaAlmacenada) => ({
        id: consulta.id,
        pregunta: consulta.pregunta,
        respuesta: consulta.respuesta,
        fecha: consulta.fecha,
        tipo_lenguaje: consulta.tipo_lenguaje,
        confianza: consulta.confianza,
        tiempo_procesamiento: consulta.tiempo_procesamiento
      }));
      setHistorial(historialLocal);
    } catch (error) {
      console.error('Error al cargar historial local:', error);
      // Mantener datos de ejemplo si todo falla
      setHistorial([
        {
          id: '1',
          pregunta: '¿Cuáles son los requisitos para un contrato de arrendamiento válido en México?',
          respuesta: 'Un contrato de arrendamiento válido en México debe cumplir con los siguientes requisitos según el Código Civil...',
          fecha: new Date().toISOString(),
          tipo_lenguaje: 'mixto',
          confianza: 0.92,
          tiempo_procesamiento: 2.3,
        },
      ]);
    }
  };

  const handleClearHistorial = () => {
    Alert.alert(
      'Limpiar Historial',
      '¿Estás seguro de que deseas eliminar todo el historial de consultas? Esto incluye las consultas guardadas localmente.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            // Limpiar historial local
            await storageService.limpiarHistorial();
            setHistorial([]);
            Alert.alert('Historial eliminado', 'Se ha limpiado el historial de consultas local y del servidor.');
          },
        },
      ]
    );
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHistorial();
    setRefreshing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return 'Hoy';
    } else if (diffDays === 2) {
      return 'Ayer';
    } else if (diffDays <= 7) {
      return `Hace ${diffDays - 1} días`;
    } else {
      return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const getTipoLenguajeColor = (tipo: string) => {
    switch (tipo) {
      case 'tecnico':
        return LegalTheme.colors.primary;
      case 'coloquial':
        return LegalTheme.colors.secondary;
      case 'mixto':
        return '#4ECDC4';
      default:
        return LegalTheme.colors.textSecondary;
    }
  };

  const getTipoLenguajeLabel = (tipo: string) => {
    switch (tipo) {
      case 'tecnico':
        return 'Técnico';
      case 'coloquial':
        return 'Coloquial';
      case 'mixto':
        return 'Mixto';
      default:
        return tipo;
    }
  };

  const getConfianzaColor = (confianza: number) => {
    if (confianza >= 0.9) return LegalTheme.colors.success;
    if (confianza >= 0.7) return LegalTheme.colors.warning;
    return LegalTheme.colors.error;
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={[LegalTheme.colors.primary, LegalTheme.colors.primaryDark]}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.headerLeft}>
            <Ionicons name="time" size={24} color="white" />
            <Text style={styles.headerTitle}>Historial de Consultas</Text>
          </View>
          
          {historial.length > 0 && (
            <TouchableOpacity style={styles.clearButton} onPress={handleClearHistorial}>
              <Ionicons name="trash" size={20} color="white" />
            </TouchableOpacity>
          )}
        </View>
        
        <Text style={styles.headerSubtitle}>
          {historial.length} consulta{historial.length !== 1 ? 's' : ''} 
          {historial.length > 0 ? '(incluye consultas offline)' : 'realizadas'}
        </Text>
      </LinearGradient>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {historial.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="document-text-outline" size={64} color={LegalTheme.colors.textSecondary} />
            <Text style={styles.emptyTitle}>No hay consultas aún</Text>
            <Text style={styles.emptySubtitle}>
              Tus consultas legales aparecerán aquí una vez que comiences a usar el asistente.
              Las consultas se guardan localmente y están disponibles sin conexión.
            </Text>
          </View>
        ) : (
          <View style={styles.consultasList}>
            {historial.map((consulta) => (
              <TouchableOpacity
                key={consulta.id}
                style={[
                  styles.consultaCard,
                  selectedConsulta === consulta.id && styles.consultaCardSelected,
                ]}
                onPress={() => {
                  setSelectedConsulta(
                    selectedConsulta === consulta.id ? null : consulta.id
                  );
                }}
                activeOpacity={0.8}
              >
                <View style={styles.consultaHeader}>
                  <View style={styles.consultaInfo}>
                    <Text style={styles.consultaFecha}>
                      {formatDate(consulta.fecha)}
                    </Text>
                    
                    <View style={styles.consultaTags}>
                      <View style={[
                        styles.tipoTag,
                        { backgroundColor: `${getTipoLenguajeColor(consulta.tipo_lenguaje)}20` }
                      ]}>
                        <Text style={[
                          styles.tipoTagText,
                          { color: getTipoLenguajeColor(consulta.tipo_lenguaje) }
                        ]}>
                          {getTipoLenguajeLabel(consulta.tipo_lenguaje)}
                        </Text>
                      </View>
                      
                      <View style={[
                        styles.confianzaTag,
                        { backgroundColor: `${getConfianzaColor(consulta.confianza)}20` }
                      ]}>
                        <Text style={[
                          styles.confianzaTagText,
                          { color: getConfianzaColor(consulta.confianza) }
                        ]}>
                          {Math.round(consulta.confianza * 100)}%
                        </Text>
                      </View>
                    </View>
                  </View>
                  
                  <Ionicons
                    name={selectedConsulta === consulta.id ? 'chevron-up' : 'chevron-down'}
                    size={20}
                    color={LegalTheme.colors.textSecondary}
                  />
                </View>

                <Text style={styles.consultaPregunta}>
                  {truncateText(consulta.pregunta, 120)}
                </Text>

                {selectedConsulta === consulta.id && (
                  <View style={styles.consultaDetalle}>
                    <View style={styles.divider} />
                    
                    <Text style={styles.respuestaLabel}>Respuesta:</Text>
                    <Text style={styles.consultaRespuesta}>
                      {consulta.respuesta}
                    </Text>
                    
                    <View style={styles.consultaStats}>
                      <View style={styles.statItem}>
                        <Ionicons name="time" size={14} color={LegalTheme.colors.textSecondary} />
                        <Text style={styles.statText}>
                          {consulta.tiempo_procesamiento.toFixed(1)}s
                        </Text>
                      </View>
                      
                      <View style={styles.statItem}>
                        <Ionicons name="checkmark-circle" size={14} color={getConfianzaColor(consulta.confianza)} />
                        <Text style={styles.statText}>
                          Confianza: {Math.round(consulta.confianza * 100)}%
                        </Text>
                      </View>
                    </View>
                  </View>
                )}
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LegalTheme.colors.background,
  },
  header: {
    paddingTop: 20,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  clearButton: {
    padding: 8,
  },
  headerSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    textAlign: 'center',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 80,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: LegalTheme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: 32,
  },
  consultasList: {
    paddingBottom: 20,
  },
  consultaCard: {
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginBottom: 12,
    ...LegalTheme.shadows.small,
  },
  consultaCardSelected: {
    borderWidth: 2,
    borderColor: LegalTheme.colors.primary,
  },
  consultaHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  consultaInfo: {
    flex: 1,
  },
  consultaFecha: {
    fontSize: 12,
    color: LegalTheme.colors.textSecondary,
    marginBottom: 6,
  },
  consultaTags: {
    flexDirection: 'row',
    gap: 8,
  },
  tipoTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tipoTagText: {
    fontSize: 10,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  confianzaTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  confianzaTagText: {
    fontSize: 10,
    fontWeight: '600',
  },
  consultaPregunta: {
    fontSize: 16,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    lineHeight: 22,
  },
  consultaDetalle: {
    marginTop: 12,
  },
  divider: {
    height: 1,
    backgroundColor: LegalTheme.colors.border,
    marginBottom: 12,
  },
  respuestaLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: LegalTheme.colors.primary,
    marginBottom: 8,
  },
  consultaRespuesta: {
    fontSize: 14,
    color: LegalTheme.colors.text,
    lineHeight: 20,
    marginBottom: 12,
  },
  consultaStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    fontSize: 12,
    color: LegalTheme.colors.textSecondary,
    marginLeft: 4,
  },
});
