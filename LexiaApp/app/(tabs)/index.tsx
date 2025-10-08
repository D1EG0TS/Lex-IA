import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  Dimensions,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { LegalChat } from '../../components/LegalChat';
import { apiService } from '../../services/apiservice';
import { LegalTheme } from '../../constants/legaltheme';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const [showChat, setShowChat] = useState(false);
  const [apiStats, setApiStats] = useState<any>(null);
  const [isApiHealthy, setIsApiHealthy] = useState(false);

  useEffect(() => {
    checkApiStatus();
    loadApiStats();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await apiService.verificarSalud();
      setIsApiHealthy(response.success);
    } catch (error) {
      setIsApiHealthy(false);
    }
  };

  const loadApiStats = async () => {
    try {
      const response = await apiService.obtenerEstadisticas();
      if (response.success) {
        setApiStats(response.data);
      }
    } catch (error) {
      console.log('No se pudieron cargar las estadísticas');
    }
  };

  const handleStartConsultation = () => {
    if (!isApiHealthy) {
      Alert.alert(
        'Servicio no disponible',
        'El servicio de consultas legales no está disponible en este momento. Por favor, intenta más tarde.',
        [{ text: 'OK' }]
      );
      return;
    }
    setShowChat(true);
  };

  const quickActions = [
    {
      id: 'civil',
      title: 'Derecho Civil',
      description: 'Contratos, propiedad, familia',
      icon: 'home',
      color: LegalTheme.colors.primary,
    },
    {
      id: 'penal',
      title: 'Derecho Penal',
      description: 'Delitos, procedimientos penales',
      icon: 'shield',
      color: LegalTheme.colors.secondary,
    },
    {
      id: 'laboral',
      title: 'Derecho Laboral',
      description: 'Trabajo, seguridad social',
      icon: 'briefcase',
      color: '#FF6B35',
    },
    {
      id: 'mercantil',
      title: 'Derecho Mercantil',
      description: 'Empresas, comercio, sociedades',
      icon: 'business',
      color: '#4ECDC4',
    },
  ];

  const recentTopics = [
    'Contratos de arrendamiento',
    'Despido injustificado',
    'Divorcio y pensión alimenticia',
    'Constitución de sociedades',
    'Delitos contra la salud',
  ];

  if (showChat) {
    return (
      <LegalChat onClose={() => setShowChat(false)} />
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Header con gradiente */}
        <LinearGradient
          colors={[LegalTheme.colors.primary, LegalTheme.colors.primaryDark]}
          style={styles.header}
        >
          <View style={styles.headerContent}>
            <View style={styles.headerTop}>
              <View style={styles.logoContainer}>
                <Image 
                  source={require('../../assets/images/logolexia1.png')} 
                  style={styles.logoImageMain}
                  resizeMode="contain"
                />
                <Text style={styles.appTitle}>LexIA</Text>
              </View>
              
              <View style={styles.statusContainer}>
                <View style={[
                  styles.statusIndicator,
                  { backgroundColor: isApiHealthy ? '#4CAF50' : '#F44336' }
                ]} />
                <Text style={styles.statusText}>
                  {isApiHealthy ? 'En línea' : 'Fuera de línea'}
                </Text>
              </View>
            </View>
            
            <Text style={styles.headerSubtitle}>
              Tu asistente legal especializado en derecho mexicano
            </Text>
            
            {apiStats && (
              <View style={styles.statsContainer}>
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>{apiStats.total_consultas || 0}</Text>
                  <Text style={styles.statLabel}>Consultas realizadas</Text>
                </View>
              </View>
            )}
          </View>
        </LinearGradient>

        {/* Botón principal de consulta */}
        <View style={styles.mainActionContainer}>
          <TouchableOpacity
            style={[
              styles.mainActionButton,
              !isApiHealthy && styles.mainActionButtonDisabled
            ]}
            onPress={handleStartConsultation}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={isApiHealthy 
                ? [LegalTheme.colors.primary, LegalTheme.colors.primaryDark]
                : ['#CCCCCC', '#999999']
              }
              style={styles.mainActionGradient}
            >
              <Ionicons 
                name="chatbubbles" 
                size={28} 
                color="white" 
              />
              <Text style={styles.mainActionText}>
                {isApiHealthy ? 'Iniciar Consulta Legal' : 'Servicio no disponible'}
              </Text>
              <Ionicons 
                name="arrow-forward" 
                size={24} 
                color="white" 
              />
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Acciones rápidas por área del derecho */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Áreas del Derecho</Text>
          <Text style={styles.sectionSubtitle}>
            Selecciona un área para obtener información específica
          </Text>
          
          <View style={styles.quickActionsGrid}>
            {quickActions.map((action) => (
              <TouchableOpacity
                key={action.id}
                style={styles.quickActionCard}
                onPress={() => {
                  if (isApiHealthy) {
                    setShowChat(true);
                  } else {
                    Alert.alert('Servicio no disponible', 'Intenta más tarde.');
                  }
                }}
                activeOpacity={0.8}
              >
                <View style={[
                  styles.quickActionIcon,
                  { backgroundColor: `${action.color}20` }
                ]}>
                  <Ionicons 
                    name={action.icon as any} 
                    size={24} 
                    color={action.color} 
                  />
                </View>
                <Text style={styles.quickActionTitle}>{action.title}</Text>
                <Text style={styles.quickActionDescription}>
                  {action.description}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Temas recientes */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Temas Frecuentes</Text>
          <Text style={styles.sectionSubtitle}>
            Consultas comunes que puedes realizar
          </Text>
          
          {recentTopics.map((topic, index) => (
            <TouchableOpacity
              key={index}
              style={styles.topicItem}
              onPress={() => {
                if (isApiHealthy) {
                  setShowChat(true);
                } else {
                  Alert.alert('Servicio no disponible', 'Intenta más tarde.');
                }
              }}
              activeOpacity={0.7}
            >
              <View style={styles.topicContent}>
                <Ionicons 
                  name="document-text" 
                  size={20} 
                  color={LegalTheme.colors.primary} 
                />
                <Text style={styles.topicText}>{topic}</Text>
              </View>
              <Ionicons 
                name="chevron-forward" 
                size={16} 
                color={LegalTheme.colors.textSecondary} 
              />
            </TouchableOpacity>
          ))}
        </View>

        {/* Información adicional */}
        <View style={styles.infoSection}>
          <View style={styles.infoCard}>
            <Image 
              source={require('../../assets/images/logolexia.png')} 
              style={styles.logoImageInfo}
              resizeMode="contain"
            />
            <View style={styles.infoContent}>
              <Text style={styles.infoTitle}>Sobre LexIA</Text>
              <Text style={styles.infoText}>
                LexIA es tu asistente legal especializado en derecho mexicano. 
                Utiliza inteligencia artificial para brindarte respuestas precisas 
                basadas en la legislación y jurisprudencia mexicana actualizada.
              </Text>
            </View>
          </View>
          
          <View style={styles.disclaimerCard}>
            <Ionicons name="warning" size={20} color={LegalTheme.colors.warning} />
            <Text style={styles.disclaimerText}>
              <Text style={styles.disclaimerBold}>Aviso importante:</Text> Las respuestas 
              proporcionadas son de carácter informativo y no constituyen asesoría legal 
              profesional. Para casos específicos, consulta con un abogado.
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LegalTheme.colors.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 32,
  },
  header: {
    paddingTop: 20,
    paddingBottom: 32,
    paddingHorizontal: 20,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    marginBottom: 16,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoImageMain: {
    width: 32,
    height: 32,
    tintColor: 'white',
  },
  logoImageInfo: {
    width: 24,
    height: 24,
    tintColor: LegalTheme.colors.primary,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginLeft: 8,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 22,
  },
  statsContainer: {
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  statLabel: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 2,
  },
  mainActionContainer: {
    paddingHorizontal: 20,
    marginTop: -16,
    marginBottom: 32,
  },
  mainActionButton: {
    borderRadius: LegalTheme.borderRadius.large,
    ...LegalTheme.shadows.large,
  },
  mainActionButtonDisabled: {
    opacity: 0.6,
  },
  mainActionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 24,
    borderRadius: LegalTheme.borderRadius.large,
  },
  mainActionText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
    marginHorizontal: 12,
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: LegalTheme.colors.text,
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: LegalTheme.colors.textSecondary,
    marginBottom: 20,
    lineHeight: 20,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    width: (width - 60) / 2,
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    ...LegalTheme.shadows.small,
  },
  quickActionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    textAlign: 'center',
    marginBottom: 4,
  },
  quickActionDescription: {
    fontSize: 12,
    color: LegalTheme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 16,
  },
  topicItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginBottom: 8,
  },
  topicContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  topicText: {
    fontSize: 15,
    color: LegalTheme.colors.text,
    marginLeft: 12,
    flex: 1,
  },
  infoSection: {
    paddingHorizontal: 20,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginBottom: 16,
    ...LegalTheme.shadows.small,
  },
  infoContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    marginBottom: 4,
  },
  infoText: {
    fontSize: 14,
    color: LegalTheme.colors.textSecondary,
    lineHeight: 20,
  },
  disclaimerCard: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255, 193, 7, 0.1)',
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: LegalTheme.colors.warning,
  },
  disclaimerText: {
    fontSize: 13,
    color: LegalTheme.colors.text,
    lineHeight: 18,
    marginLeft: 8,
    flex: 1,
  },
  disclaimerBold: {
    fontWeight: '600',
  },
});
