import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Linking,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { LegalTheme } from '../constants/legaltheme';
import { DocumentoLegal } from '../services/apiservice';

interface DocumentoLegalCardProps {
  documento: DocumentoLegal;
  onPress?: (documento: DocumentoLegal) => void;
}

export const DocumentoLegalCard: React.FC<DocumentoLegalCardProps> = ({ 
  documento, 
  onPress 
}) => {
  const handlePress = () => {
    if (onPress) {
      onPress(documento);
    } else if (documento.url) {
      handleOpenUrl();
    }
  };

  const handleOpenUrl = async () => {
    if (!documento.url) return;

    try {
      const supported = await Linking.canOpenURL(documento.url);
      if (supported) {
        await Linking.openURL(documento.url);
      } else {
        Alert.alert(
          'Error',
          'No se puede abrir este enlace en tu dispositivo',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      Alert.alert(
        'Error',
        'Ocurrió un error al intentar abrir el enlace',
        [{ text: 'OK' }]
      );
    }
  };

  const getDocumentIcon = (tipo: string) => {
    switch (tipo.toLowerCase()) {
      case 'ley':
      case 'código':
        return 'library';
      case 'reglamento':
        return 'document-text';
      case 'jurisprudencia':
        return 'hammer';
      case 'tesis':
        return 'school';
      case 'decreto':
        return 'ribbon';
      default:
        return 'document';
    }
  };

  const getRelevanceColor = (relevancia: number) => {
    if (relevancia >= 0.8) return LegalTheme.colors.success;
    if (relevancia >= 0.6) return LegalTheme.colors.warning;
    return LegalTheme.colors.error;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Fecha no disponible';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return 'Fecha no válida';
    }
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <TouchableOpacity 
      style={styles.container} 
      onPress={handlePress}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={[
          'rgba(255, 255, 255, 0.9)',
          'rgba(248, 250, 252, 0.9)',
        ]}
        style={styles.gradient}
      >
        {/* Header con icono y tipo */}
        <View style={styles.header}>
          <View style={styles.iconContainer}>
            <Ionicons 
              name={getDocumentIcon(documento.tipo)} 
              size={20} 
              color={LegalTheme.colors.primary} 
            />
          </View>
          
          <View style={styles.headerText}>
            <Text style={styles.tipo}>{documento.tipo.toUpperCase()}</Text>
            <Text style={styles.fuente}>{documento.fuente}</Text>
          </View>
          
          {/* Indicador de relevancia */}
          <View style={[
            styles.relevanceIndicator,
            { backgroundColor: getRelevanceColor(documento.relevancia) }
          ]}>
            <Text style={styles.relevanceText}>
              {Math.round(documento.relevancia * 100)}%
            </Text>
          </View>
        </View>

        {/* Título del documento */}
        <Text style={styles.titulo}>
          {truncateText(documento.titulo, 80)}
        </Text>

        {/* Fragmento relevante */}
        {documento.fragmento && (
          <View style={styles.fragmentContainer}>
            <Text style={styles.fragmentLabel}>Fragmento relevante:</Text>
            <Text style={styles.fragmento}>
              {truncateText(documento.fragmento, 150)}
            </Text>
          </View>
        )}

        {/* Artículo específico */}
        {documento.articulo && (
          <View style={styles.articuloContainer}>
            <Ionicons name="bookmark" size={14} color={LegalTheme.colors.primary} />
            <Text style={styles.articulo}>
              {documento.articulo}
            </Text>
          </View>
        )}

        {/* Footer con fecha y enlace */}
        <View style={styles.footer}>
          <View style={styles.dateContainer}>
            <Ionicons name="calendar" size={12} color={LegalTheme.colors.textSecondary} />
            <Text style={styles.fecha}>
              {formatDate(documento.fecha_publicacion)}
            </Text>
          </View>
          
          {documento.url && (
            <View style={styles.linkContainer}>
              <Ionicons name="link" size={12} color={LegalTheme.colors.primary} />
              <Text style={styles.linkText}>Ver documento</Text>
            </View>
          )}
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    width: 280,
    marginRight: 12,
    borderRadius: LegalTheme.borderRadius.medium,
    ...LegalTheme.shadows.medium,
  },
  gradient: {
    padding: 16,
    borderRadius: LegalTheme.borderRadius.medium,
    borderWidth: 1,
    borderColor: LegalTheme.colors.border,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(0, 104, 71, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  headerText: {
    flex: 1,
  },
  tipo: {
    fontSize: 12,
    fontWeight: '700',
    color: LegalTheme.colors.primary,
    letterSpacing: 0.5,
  },
  fuente: {
    fontSize: 11,
    color: LegalTheme.colors.textSecondary,
    marginTop: 2,
  },
  relevanceIndicator: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 45,
    alignItems: 'center',
  },
  relevanceText: {
    fontSize: 10,
    fontWeight: '600',
    color: 'white',
  },
  titulo: {
    fontSize: 14,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    lineHeight: 20,
    marginBottom: 8,
  },
  fragmentContainer: {
    backgroundColor: 'rgba(0, 104, 71, 0.05)',
    padding: 8,
    borderRadius: LegalTheme.borderRadius.small,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: LegalTheme.colors.primary,
  },
  fragmentLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: LegalTheme.colors.primary,
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  fragmento: {
    fontSize: 12,
    color: LegalTheme.colors.text,
    lineHeight: 16,
    fontStyle: 'italic',
  },
  articuloContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: 'rgba(206, 17, 38, 0.1)',
    borderRadius: LegalTheme.borderRadius.small,
  },
  articulo: {
    fontSize: 12,
    fontWeight: '500',
    color: LegalTheme.colors.secondary,
    marginLeft: 4,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: LegalTheme.colors.border,
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  fecha: {
    fontSize: 10,
    color: LegalTheme.colors.textSecondary,
    marginLeft: 4,
  },
  linkContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  linkText: {
    fontSize: 10,
    color: LegalTheme.colors.primary,
    fontWeight: '500',
    marginLeft: 4,
  },
});