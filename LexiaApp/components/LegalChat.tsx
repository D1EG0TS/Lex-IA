import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  Text,
  TouchableOpacity,
  ScrollView,
  Image,
} from 'react-native';
import Chat from '@codsod/react-native-chat';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

import { apiService, ConsultaLegal, RespuestaLegal } from '../services/apiservice';
import { LegalTheme } from '../constants/legaltheme';
import { LegalLoadingIndicator } from './legalloadingindicator';
import { DocumentoLegalCard } from './DocumentoLegalCard';
import { ConfiguracionConsulta } from './ConfiguracionConsulta';
import { storageService } from '../services/storageService';

// Interfaz para mensajes con metadata personalizada
interface LegalMessage {
  _id: string | number;
  text: string;
  createdAt: Date;
  user: {
    _id: string | number;
    name: string;
    avatar?: string;
  };
  system?: boolean;
  metadata?: {
    fundamentos?: any[];
    confianza?: number;
    advertencias?: string[];
    sugerencias?: string[];
    tiempo_procesamiento?: number;
  };
}

interface LegalChatProps {
  onClose?: () => void;
}

export const LegalChat: React.FC<LegalChatProps> = ({ onClose }) => {
  const [messages, setMessages] = useState<LegalMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const [showConfig, setShowConfig] = useState(false);
  const [consultaConfig, setConsultaConfig] = useState<Partial<ConsultaLegal>>({
    tipo_lenguaje: 'mixto',
    incluir_fundamentos: true,
    max_documentos: 5,
    umbral_relevancia: 0.7,
    incluir_metadatos: true,
  });

  useEffect(() => {
    // Mensaje de bienvenida
    setMessages([
      {
        _id: 'welcome',
        text: '¡Hola! Soy tu asistente legal especializado en derecho mexicano. Puedo ayudarte con consultas sobre leyes, reglamentos, códigos y jurisprudencia mexicana. ¿En qué puedo asistirte hoy?',
        createdAt: new Date(),
        user: {
          _id: 'assistant',
          name: 'Asistente Legal',
          avatar: '⚖️',
        },
        system: true,
      },
    ]);

    // Verificar conexión con la API
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await apiService.verificarSalud();
      setIsConnected(response.success);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const onSendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    const userMessage: LegalMessage = {
      _id: Date.now().toString(),
      text: text.trim(),
      createdAt: new Date(),
      user: {
        _id: 'user',
        name: 'Usuario',
        avatar: '👤',
      },
    };

    // Agregar mensaje del usuario
    setMessages((prevMessages) => [userMessage, ...prevMessages]);
    setIsLoading(true);

    try {
      const consulta: ConsultaLegal = {
        pregunta: text,
        ...consultaConfig,
      };

      const response = await apiService.realizarConsulta(consulta);

      if (response.success && response.data) {
        const respuestaLegal = response.data;
        
        // Guardar la consulta y respuesta localmente
        await storageService.guardarConsulta(consulta, respuestaLegal);
        
        // Crear mensaje de respuesta con metadata
        const assistantMessage: LegalMessage = {
          _id: (Date.now() + 1).toString(),
          text: respuestaLegal.respuesta,
          createdAt: new Date(),
          user: {
            _id: 'assistant',
            name: 'Asistente Legal',
            avatar: '⚖️',
          },
          metadata: {
            fundamentos: respuestaLegal.fundamentos_legales,
            confianza: respuestaLegal.confianza,
            advertencias: respuestaLegal.advertencias,
            sugerencias: respuestaLegal.sugerencias,
            tiempo_procesamiento: respuestaLegal.tiempo_procesamiento,
          },
        };

        setMessages((prevMessages) => [assistantMessage, ...prevMessages]);

        // Mostrar advertencias si las hay
        if (respuestaLegal.advertencias.length > 0) {
          setTimeout(() => {
            Alert.alert(
              'Advertencias',
              respuestaLegal.advertencias.join('\n'),
              [{ text: 'Entendido' }]
            );
          }, 1000);
        }
      } else {
        // Error en la consulta - también guardar localmente para referencia
        const consultaError = {
          pregunta: text,
          ...consultaConfig,
        };
        
        const respuestaError = {
          respuesta: `Error: ${response.error}`,
          tipo_lenguaje_usado: consultaConfig.tipo_lenguaje || 'mixto' as const,
          fundamentos_legales: [],
          confianza: 0,
          advertencias: ['Error de conexión'],
          sugerencias: ['Intenta nuevamente cuando tengas conexión'],
          tiempo_procesamiento: 0,
          timestamp: new Date().toISOString()
        };
        
        await storageService.guardarConsulta(consultaError, respuestaError);
        
        const errorMessage: LegalMessage = {
          _id: (Date.now() + 1).toString(),
          text: `Lo siento, ocurrió un error al procesar tu consulta: ${response.error}`,
          createdAt: new Date(),
          user: {
            _id: 'system',
            name: 'Sistema',
            avatar: '⚠️',
          },
          system: true,
        };

        setMessages((prevMessages) => [errorMessage, ...prevMessages]);
      }
    } catch (error) {
      console.error('Error en consulta:', error);
      
      // Guardar consulta fallida localmente
      const consultaError = {
        pregunta: text,
        ...consultaConfig,
      };
      
      const respuestaError = {
        respuesta: 'Error de conexión - consulta guardada localmente',
        tipo_lenguaje_usado: consultaConfig.tipo_lenguaje || 'mixto' as const,
        fundamentos_legales: [],
        confianza: 0,
        advertencias: ['Sin conexión al servidor'],
        sugerencias: ['La consulta se ha guardado y se procesará cuando haya conexión'],
        tiempo_procesamiento: 0,
        timestamp: new Date().toISOString()
      };
      
      await storageService.guardarConsulta(consultaError, respuestaError);
      
      const errorMessage: LegalMessage = {
        _id: (Date.now() + 1).toString(),
        text: 'Lo siento, no pude procesar tu consulta en este momento. Se ha guardado localmente y se procesará cuando haya conexión.',
        createdAt: new Date(),
        user: {
          _id: 'system',
          name: 'Sistema',
          avatar: '⚠️',
        },
        system: true,
      };

      setMessages((prevMessages) => [errorMessage, ...prevMessages]);
    } finally {
      setIsLoading(false);
    }
  }, [consultaConfig]);

  // Componente personalizado para renderizar mensajes con fundamentos legales
  const renderCustomMessage = (message: LegalMessage) => {
    const isUser = message.user._id === 'user';
    const isSystem = message.user._id === 'system';
    
    return (
      <View key={message._id} style={styles.messageContainer}>
        {/* Mensaje principal */}
        <View style={[
          styles.messageBubble,
          isUser ? styles.userBubble : isSystem ? styles.systemBubble : styles.assistantBubble
        ]}>
          <Text style={[
            styles.messageText,
            isUser ? styles.userText : styles.assistantText
          ]}>
            {message.text}
          </Text>
          
          {/* Avatar y nombre */}
          {!isUser && (
            <View style={styles.messageInfo}>
              <Text style={styles.messageAvatar}>{message.user.avatar}</Text>
              <Text style={styles.messageName}>{message.user.name}</Text>
            </View>
          )}
        </View>
        
        {/* Mostrar fundamentos legales si existen */}
        {message.metadata?.fundamentos && message.metadata.fundamentos.length > 0 && (
          <View style={styles.fundamentosContainer}>
            <Text style={styles.fundamentosTitle}>Fundamentos Legales:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {message.metadata.fundamentos.map((doc: any, index: number) => (
                <DocumentoLegalCard key={index} documento={doc} />
              ))}
            </ScrollView>
            
            {/* Mostrar nivel de confianza */}
            <View style={styles.confianzaContainer}>
              <Text style={styles.confianzaText}>
                Nivel de confianza: {Math.round((message.metadata?.confianza || 0) * 100)}%
              </Text>
            </View>
          </View>
        )}
      </View>
    );
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
            <Image 
              source={require('../assets/images/logolexia1.png')} 
              style={styles.logoImage}
              resizeMode="contain"
            />
            <Text style={styles.headerTitle}>Lexia</Text>
          </View>
          
          <View style={styles.headerRight}>
            {!isConnected && (
              <Ionicons name="warning" size={20} color={LegalTheme.colors.warning} />
            )}
            
            <TouchableOpacity
              style={styles.configButton}
              onPress={() => setShowConfig(!showConfig)}
            >
              <Ionicons name="settings" size={20} color="white" />
            </TouchableOpacity>
            
            {onClose && (
              <TouchableOpacity style={styles.closeButton} onPress={onClose}>
                <Ionicons name="close" size={24} color="white" />
              </TouchableOpacity>
            )}
          </View>
        </View>
        
        {!isConnected && (
          <Text style={styles.connectionWarning}>
            ⚠️ Sin conexión con el servidor
          </Text>
        )}
      </LinearGradient>

      {/* Configuración */}
      {showConfig && (
        <ConfiguracionConsulta
          config={consultaConfig}
          onConfigChange={setConsultaConfig}
          onClose={() => setShowConfig(false)}
        />
      )}

      {/* Chat Container */}
      <KeyboardAvoidingView 
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0} // Ajustar offset
      >
        <View style={styles.chatWrapper}>
          {/* Mensajes personalizados con fundamentos legales */}
          {/* En la línea 280-300, modifica el ScrollView de mensajes: */}
          <ScrollView 
            style={styles.messagesContainer}
            contentContainerStyle={{
              ...styles.messagesContent,
              flexDirection: 'column-reverse',
              flexGrow: 1, // Permitir que el contenido crezca
              minHeight: '100%', // Asegurar que use todo el espacio disponible
            }}
            showsVerticalScrollIndicator={true}
            keyboardShouldPersistTaps="handled"
            maintainVisibleContentPosition={{
              minIndexForVisible: 0,
              autoscrollToTopThreshold: 10,
            }}
          >
            {messages.map((message) => renderCustomMessage(message))}
          </ScrollView>
          
          {/* Chat UI Component */}
          <View style={styles.chatInputContainer}>
            <Chat
              messages={[]} // Usamos nuestro renderizado personalizado arriba
              setMessages={onSendMessage}
              themeColor={LegalTheme.colors.primary}
              themeTextColor="white"
              showSenderAvatar={false}
              showReceiverAvatar={false}
              inputBorderColor={LegalTheme.colors.primary}
              user={{
                _id: 1,
                name: 'Usuario',
              }}
              backgroundColor={LegalTheme.colors.background}
              inputBackgroundColor={LegalTheme.colors.surface}
              placeholder="Escribe tu consulta legal..."
              placeholderColor={LegalTheme.colors.textSecondary}
              showEmoji={false}
              showAttachment={false}
              style={styles.chatInput} // Agregar estilo personalizado
            />
          </View>
        </View>
        
        {isLoading && <LegalLoadingIndicator />}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LegalTheme.colors.background,
  },
  header: {
    paddingTop: Platform.OS === 'ios' ? 0 : 20,
    paddingBottom: 16,
    paddingHorizontal: 16,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  configButton: {
    padding: 8,
    marginRight: 8,
  },
  closeButton: {
    padding: 4,
  },
  connectionWarning: {
    color: LegalTheme.colors.warning,
    fontSize: 12,
    textAlign: 'center',
    marginTop: 8,
  },
  chatContainer: {
    flex: 1, // Mantener flex: 1 para usar todo el espacio disponible
  },
  chatWrapper: {
    flex: 1,
    paddingBottom: 0, // Eliminar padding inferior
  },
  messagesContainer: {
    flex: 1,
    paddingHorizontal: 16,
    marginBottom: 0, // Eliminar margen inferior
  },
  messagesContent: {
    paddingVertical: 8,
    paddingBottom: 10, // Reducir aún más el padding inferior
  },
  chatInputContainer: {
    minHeight: 150, // Altura mínima para el contenedor del input
    maxHeight: 100, // Altura máxima para evitar que crezca demasiado
    paddingHorizontal: 10,
    paddingVertical: 5,
    backgroundColor: LegalTheme.colors.background,
  },
  chatInput: {
    minHeight: 50, // Altura mínima del input
    maxHeight: 80, // Altura máxima del input
  },
  messageContainer: {
    marginVertical: 4,
  },
  messageBubble: {
    padding: 12,
    borderRadius: LegalTheme.borderRadius.medium,
    maxWidth: '80%',
  },
  userBubble: {
    backgroundColor: LegalTheme.colors.userMessage,
    alignSelf: 'flex-end',
  },
  assistantBubble: {
    backgroundColor: LegalTheme.colors.assistantMessage,
    alignSelf: 'flex-start',
  },
  systemBubble: {
    backgroundColor: LegalTheme.colors.systemMessage,
    alignSelf: 'center',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: LegalTheme.colors.text,
  },
  assistantText: {
    color: LegalTheme.colors.text,
  },
  messageInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  messageAvatar: {
    fontSize: 12,
    marginRight: 4,
  },
  messageName: {
    fontSize: 10,
    color: LegalTheme.colors.textSecondary,
    fontStyle: 'italic',
  },
  fundamentosContainer: {
    marginTop: 8,
    marginHorizontal: 16,
    padding: 12,
    backgroundColor: LegalTheme.colors.surfaceVariant,
    borderRadius: LegalTheme.borderRadius.medium,
  },
  fundamentosTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    marginBottom: 8,
  },
  confianzaContainer: {
    marginTop: 8,
    alignItems: 'center',
  },
  confianzaText: {
    fontSize: 12,
    color: LegalTheme.colors.textSecondary,
    fontStyle: 'italic',
  },
  logoImage: {
    width: 24,
    height: 24,
    tintColor: 'white', // Esto hará que el logo sea blanco para que se vea bien en el fondo oscuro
  },
});