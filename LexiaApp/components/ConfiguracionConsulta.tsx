import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Switch,
  ScrollView,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { LegalTheme } from '../constants/legaltheme';
import { ConsultaLegal } from '../services/apiservice';

interface ConfiguracionConsultaProps {
  config: Partial<ConsultaLegal>;
  onConfigChange: (config: Partial<ConsultaLegal>) => void;
  onClose: () => void;
}

export const ConfiguracionConsulta: React.FC<ConfiguracionConsultaProps> = ({
  config,
  onConfigChange,
  onClose,
}) => {
  const updateConfig = (key: keyof ConsultaLegal, value: any) => {
    onConfigChange({
      ...config,
      [key]: value,
    });
  };

  const tiposLenguaje = [
    { value: 'tecnico', label: 'Técnico', description: 'Lenguaje jurídico formal' },
    { value: 'coloquial', label: 'Coloquial', description: 'Lenguaje simple y claro' },
    { value: 'mixto', label: 'Mixto', description: 'Combinación equilibrada' },
  ];

  const nivelesDocumentos = [
    { value: 3, label: '3 documentos', description: 'Respuesta concisa' },
    { value: 5, label: '5 documentos', description: 'Respuesta balanceada' },
    { value: 8, label: '8 documentos', description: 'Respuesta detallada' },
    { value: 10, label: '10 documentos', description: 'Análisis exhaustivo' },
  ];

  const nivelesRelevancia = [
    { value: 0.5, label: 'Baja (50%)', description: 'Incluye más documentos' },
    { value: 0.7, label: 'Media (70%)', description: 'Balance recomendado' },
    { value: 0.8, label: 'Alta (80%)', description: 'Solo muy relevantes' },
    { value: 0.9, label: 'Muy Alta (90%)', description: 'Extremadamente selectivo' },
  ];

  return (
    <Modal
      visible={true}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <LinearGradient
          colors={[LegalTheme.colors.primary, LegalTheme.colors.primaryDark]}
          style={styles.header}
        >
          <View style={styles.headerContent}>
            <View style={styles.headerLeft}>
              <Ionicons name="settings" size={24} color="white" />
              <Text style={styles.headerTitle}>Configuración de Consulta</Text>
            </View>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color="white" />
            </TouchableOpacity>
          </View>
        </LinearGradient>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Tipo de Lenguaje */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Tipo de Lenguaje</Text>
            <Text style={styles.sectionDescription}>
              Selecciona el estilo de respuesta que prefieres
            </Text>
            
            {tiposLenguaje.map((tipo) => (
              <TouchableOpacity
                key={tipo.value}
                style={[
                  styles.optionCard,
                  config.tipo_lenguaje === tipo.value && styles.optionCardSelected,
                ]}
                onPress={() => updateConfig('tipo_lenguaje', tipo.value)}
              >
                <View style={styles.optionContent}>
                  <View style={styles.optionHeader}>
                    <Text style={[
                      styles.optionTitle,
                      config.tipo_lenguaje === tipo.value && styles.optionTitleSelected,
                    ]}>
                      {tipo.label}
                    </Text>
                    <View style={[
                      styles.radioButton,
                      config.tipo_lenguaje === tipo.value && styles.radioButtonSelected,
                    ]}>
                      {config.tipo_lenguaje === tipo.value && (
                        <View style={styles.radioButtonInner} />
                      )}
                    </View>
                  </View>
                  <Text style={styles.optionDescription}>{tipo.description}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>

          {/* Número de Documentos */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Número de Documentos</Text>
            <Text style={styles.sectionDescription}>
              Cantidad máxima de documentos legales a consultar
            </Text>
            
            {nivelesDocumentos.map((nivel) => (
              <TouchableOpacity
                key={nivel.value}
                style={[
                  styles.optionCard,
                  config.max_documentos === nivel.value && styles.optionCardSelected,
                ]}
                onPress={() => updateConfig('max_documentos', nivel.value)}
              >
                <View style={styles.optionContent}>
                  <View style={styles.optionHeader}>
                    <Text style={[
                      styles.optionTitle,
                      config.max_documentos === nivel.value && styles.optionTitleSelected,
                    ]}>
                      {nivel.label}
                    </Text>
                    <View style={[
                      styles.radioButton,
                      config.max_documentos === nivel.value && styles.radioButtonSelected,
                    ]}>
                      {config.max_documentos === nivel.value && (
                        <View style={styles.radioButtonInner} />
                      )}
                    </View>
                  </View>
                  <Text style={styles.optionDescription}>{nivel.description}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>

          {/* Umbral de Relevancia */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Umbral de Relevancia</Text>
            <Text style={styles.sectionDescription}>
              Nivel mínimo de relevancia para incluir documentos
            </Text>
            
            {nivelesRelevancia.map((nivel) => (
              <TouchableOpacity
                key={nivel.value}
                style={[
                  styles.optionCard,
                  config.umbral_relevancia === nivel.value && styles.optionCardSelected,
                ]}
                onPress={() => updateConfig('umbral_relevancia', nivel.value)}
              >
                <View style={styles.optionContent}>
                  <View style={styles.optionHeader}>
                    <Text style={[
                      styles.optionTitle,
                      config.umbral_relevancia === nivel.value && styles.optionTitleSelected,
                    ]}>
                      {nivel.label}
                    </Text>
                    <View style={[
                      styles.radioButton,
                      config.umbral_relevancia === nivel.value && styles.radioButtonSelected,
                    ]}>
                      {config.umbral_relevancia === nivel.value && (
                        <View style={styles.radioButtonInner} />
                      )}
                    </View>
                  </View>
                  <Text style={styles.optionDescription}>{nivel.description}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>

          {/* Opciones Adicionales */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Opciones Adicionales</Text>
            
            {/* Incluir Fundamentos */}
            <View style={styles.switchOption}>
              <View style={styles.switchContent}>
                <Ionicons name="library" size={20} color={LegalTheme.colors.primary} />
                <View style={styles.switchText}>
                  <Text style={styles.switchTitle}>Incluir Fundamentos Legales</Text>
                  <Text style={styles.switchDescription}>
                    Mostrar documentos que respaldan la respuesta
                  </Text>
                </View>
              </View>
              <Switch
                value={config.incluir_fundamentos || false}
                onValueChange={(value) => updateConfig('incluir_fundamentos', value)}
                trackColor={{ 
                  false: LegalTheme.colors.border, 
                  true: LegalTheme.colors.primary 
                }}
                thumbColor={config.incluir_fundamentos ? 'white' : LegalTheme.colors.textSecondary}
              />
            </View>

            {/* Incluir Metadatos */}
            <View style={styles.switchOption}>
              <View style={styles.switchContent}>
                <Ionicons name="information-circle" size={20} color={LegalTheme.colors.primary} />
                <View style={styles.switchText}>
                  <Text style={styles.switchTitle}>Incluir Metadatos</Text>
                  <Text style={styles.switchDescription}>
                    Información adicional sobre los documentos
                  </Text>
                </View>
              </View>
              <Switch
                value={config.incluir_metadatos || false}
                onValueChange={(value) => updateConfig('incluir_metadatos', value)}
                trackColor={{ 
                  false: LegalTheme.colors.border, 
                  true: LegalTheme.colors.primary 
                }}
                thumbColor={config.incluir_metadatos ? 'white' : LegalTheme.colors.textSecondary}
              />
            </View>
          </View>

          {/* Botón de Restaurar Valores por Defecto */}
          <TouchableOpacity
            style={styles.resetButton}
            onPress={() => {
              onConfigChange({
                tipo_lenguaje: 'mixto',
                incluir_fundamentos: true,
                max_documentos: 5,
                umbral_relevancia: 0.7,
                incluir_metadatos: true,
              });
            }}
          >
            <Ionicons name="refresh" size={20} color={LegalTheme.colors.textSecondary} />
            <Text style={styles.resetButtonText}>Restaurar valores por defecto</Text>
          </TouchableOpacity>
        </ScrollView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LegalTheme.colors.background,
  },
  header: {
    paddingTop: 50,
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
    flex: 1,
  },
  headerTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  closeButton: {
    padding: 4,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: LegalTheme.colors.text,
    marginBottom: 4,
  },
  sectionDescription: {
    fontSize: 14,
    color: LegalTheme.colors.textSecondary,
    marginBottom: 16,
    lineHeight: 20,
  },
  optionCard: {
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginBottom: 8,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  optionCardSelected: {
    borderColor: LegalTheme.colors.primary,
    backgroundColor: 'rgba(0, 104, 71, 0.05)',
  },
  optionContent: {
    flex: 1,
  },
  optionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: LegalTheme.colors.text,
  },
  optionTitleSelected: {
    color: LegalTheme.colors.primary,
  },
  optionDescription: {
    fontSize: 14,
    color: LegalTheme.colors.textSecondary,
    lineHeight: 18,
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: LegalTheme.colors.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioButtonSelected: {
    borderColor: LegalTheme.colors.primary,
  },
  radioButtonInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: LegalTheme.colors.primary,
  },
  switchOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginBottom: 8,
  },
  switchContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  switchText: {
    marginLeft: 12,
    flex: 1,
  },
  switchTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    marginBottom: 2,
  },
  switchDescription: {
    fontSize: 14,
    color: LegalTheme.colors.textSecondary,
    lineHeight: 18,
  },
  resetButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: LegalTheme.colors.surface,
    borderRadius: LegalTheme.borderRadius.medium,
    padding: 16,
    marginTop: 16,
    marginBottom: 32,
  },
  resetButtonText: {
    fontSize: 16,
    color: LegalTheme.colors.textSecondary,
    marginLeft: 8,
    fontWeight: '500',
  },
});