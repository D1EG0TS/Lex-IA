import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { LegalTheme } from '../constants/legaltheme';

interface LegalLoadingIndicatorProps {
  message?: string;
}

export const LegalLoadingIndicator: React.FC<LegalLoadingIndicatorProps> = ({ 
  message = 'Analizando consulta legal...' 
}) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;
  const opacityAnim = useRef(new Animated.Value(0.3)).current;
  const dotAnim1 = useRef(new Animated.Value(0)).current;
  const dotAnim2 = useRef(new Animated.Value(0)).current;
  const dotAnim3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Animación de escala pulsante
    const scaleAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );

    // Animación de rotación
    const rotateAnimation = Animated.loop(
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: true,
      })
    );

    // Animación de opacidad
    const opacityAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );

    // Animación de puntos secuencial
    const dotAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(dotAnim1, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(dotAnim2, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(dotAnim3, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(dotAnim1, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(dotAnim2, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(dotAnim3, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
      ])
    );

    scaleAnimation.start();
    rotateAnimation.start();
    opacityAnimation.start();
    dotAnimation.start();

    return () => {
      scaleAnimation.stop();
      rotateAnimation.stop();
      opacityAnimation.stop();
      dotAnimation.stop();
    };
  }, []);

  const spin = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.overlay}>
      <LinearGradient
        colors={[
          'rgba(0, 0, 0, 0.1)',
          'rgba(0, 0, 0, 0.3)',
          'rgba(0, 0, 0, 0.1)',
        ]}
        style={styles.container}
      >
        <View style={styles.loadingContent}>
          {/* Icono principal animado */}
          <Animated.View
            style={[
              styles.iconContainer,
              {
                transform: [
                  { scale: scaleAnim },
                  { rotate: spin },
                ],
                opacity: opacityAnim,
              },
            ]}
          >
            <Ionicons 
              name="scale"
              size={40} 
              color={LegalTheme.colors.primary} 
            />
          </Animated.View>

          {/* Círculo de progreso */}
          <View style={styles.progressRing}>
            <Animated.View
              style={[
                styles.progressIndicator,
                {
                  transform: [{ rotate: spin }],
                },
              ]}
            />
          </View>

          {/* Mensaje de carga */}
          <Text style={styles.loadingText}>{message}</Text>

          {/* Puntos animados */}
          <View style={styles.dotsContainer}>
            <Animated.View
              style={[
                styles.dot,
                {
                  opacity: dotAnim1,
                  transform: [{ scale: dotAnim1 }],
                },
              ]}
            />
            <Animated.View
              style={[
                styles.dot,
                {
                  opacity: dotAnim2,
                  transform: [{ scale: dotAnim2 }],
                },
              ]}
            />
            <Animated.View
              style={[
                styles.dot,
                {
                  opacity: dotAnim3,
                  transform: [{ scale: dotAnim3 }],
                },
              ]}
            />
          </View>

          {/* Texto adicional */}
          <Text style={styles.subText}>
            Consultando base de datos legal mexicana
          </Text>
        </View>
      </LinearGradient>
    </View>
  );
};

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  container: {
    width: width * 0.8,
    maxWidth: 300,
    padding: 32,
    borderRadius: LegalTheme.borderRadius.large,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    alignItems: 'center',
    ...LegalTheme.shadows.large,
  },
  loadingContent: {
    alignItems: 'center',
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(0, 104, 71, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  progressRing: {
    position: 'absolute',
    top: 0,
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 2,
    borderColor: 'rgba(0, 104, 71, 0.2)',
  },
  progressIndicator: {
    position: 'absolute',
    top: -2,
    left: -2,
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 2,
    borderColor: 'transparent',
    borderTopColor: LegalTheme.colors.primary,
    borderRightColor: LegalTheme.colors.primary,
  },
  loadingText: {
    fontSize: 16,
    fontWeight: '600',
    color: LegalTheme.colors.text,
    textAlign: 'center',
    marginTop: 24,
    marginBottom: 16,
  },
  dotsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: LegalTheme.colors.primary,
    marginHorizontal: 4,
  },
  subText: {
    fontSize: 12,
    color: LegalTheme.colors.textSecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});