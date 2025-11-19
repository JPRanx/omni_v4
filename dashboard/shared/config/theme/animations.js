/**
 * Dashboard V3 - Animation System
 *
 * Complete animation configuration based on comprehensive audit
 * Total Configurations: 48
 *
 * Breakdown:
 * - Keyframe Animations: 15
 * - Transition Variables: 5
 * - Hover Effects: 18
 * - Stagger Delays: 2 patterns
 * - Reduced Motion Fallbacks: 7 sections
 * - Performance Hints: GPU acceleration
 *
 * Source Files Analyzed:
 * - theme.css (lines 44-98, 258-267)
 * - dashboard_generator.py (lines 208-214, 574-933, 1318-1683)
 */

import { conflicts } from '../resolution.js';

// ============================================
// KEYFRAME DEFINITIONS (15 animations)
// ============================================

export const keyframes = {
  // Gloss/Shine Effects
  slideGloss: {
    name: 'slideGloss',
    keyframes: {
      '0%': { backgroundPosition: '-200% center' },
      '100%': { backgroundPosition: '200% center' },
    },
    duration: '3s',
    timing: 'linear',
    iteration: 'infinite',
  },

  slideGlossFast: {
    name: 'slideGlossFast',
    keyframes: {
      '0%': { backgroundPosition: '-200% center' },
      '100%': { backgroundPosition: '200% center' },
    },
    duration: '8s',
    timing: 'linear',
    iteration: 'infinite',
  },

  // Alert/Warning Pulse
  bottleneckPulse: {
    name: 'bottleneckPulse',
    keyframes: {
      '0%, 100%': { opacity: 1 },
      '50%': { opacity: 0.7 },
    },
    duration: '2s',
    timing: 'ease-in-out',
    iteration: 'infinite',
  },

  // Fade Ins
  fadeIn: {
    name: 'fadeIn',
    keyframes: {
      from: { opacity: 0, transform: 'translateY(10px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
    duration: 'var(--transition-base)',
    timing: 'ease-out',
  },

  // Loading States
  shimmer: {
    name: 'shimmer',
    keyframes: {
      '0%': { backgroundPosition: '-1000px 0' },
      '100%': { backgroundPosition: '1000px 0' },
    },
    duration: '2s',
    timing: 'infinite',
  },

  // Progress Bars
  scoreBarShine: {
    name: 'scoreBarShine',
    keyframes: {
      '0%': { left: '-100%' },
      '50%': { left: '100%' },
      '100%': { left: '100%' },
    },
    duration: '2s',
    timing: 'ease-in-out',
    iteration: 'infinite',
  },

  // Ambient Body Effects
  luxuryShimmer: {
    name: 'luxuryShimmer',
    keyframes: {
      '0%, 100%': { opacity: 0.03 },
      '50%': { opacity: 0.08 },
    },
    duration: '15s',
    timing: 'ease-in-out',
    iteration: 'infinite',
  },

  slowRotate: {
    name: 'slowRotate',
    keyframes: {
      from: { transform: 'rotate(0deg)' },
      to: { transform: 'rotate(360deg)' },
    },
    duration: '40s',
    timing: 'linear',
    iteration: 'infinite',
  },

  // Title Animations
  titleFadeIn: {
    name: 'titleFadeIn',
    keyframes: {
      from: { opacity: 0, transform: 'translateY(-20px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
    duration: '0.8s',
    timing: 'cubic-bezier(0.16, 1, 0.3, 1)',
  },

  subtitleFadeIn: {
    name: 'subtitleFadeIn',
    keyframes: {
      from: { opacity: 0, transform: 'translateX(-10px)' },
      to: { opacity: 1, transform: 'translateX(0)' },
    },
    duration: '0.8s',
    timing: 'ease',
    delay: '0.2s',
  },

  // Page Transitions
  contentFadeIn: {
    name: 'contentFadeIn',
    keyframes: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    duration: '0.6s',
    timing: 'ease',
  },

  elegantFadeIn: {
    name: 'elegantFadeIn',
    keyframes: {
      from: { opacity: 0, transform: 'translateY(5px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
    duration: '0.5s',
    timing: 'ease',
  },

  // Component-Specific
  metricFadeIn: {
    name: 'metricFadeIn',
    keyframes: {
      from: { opacity: 0, transform: 'translateY(8px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
    duration: '0.5s',
    timing: 'ease',
  },

  cardFadeIn: {
    name: 'cardFadeIn',
    keyframes: {
      from: { opacity: 0, transform: 'scale(0.95)' },
      to: { opacity: 1, transform: 'scale(1)' },
    },
    duration: '0.6s',
    timing: 'ease',
  },

  // Modal Animations
  modalFadeIn: {
    name: 'modalFadeIn',
    keyframes: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    duration: '0.35s',
    timing: 'ease',
  },

  modalSlideUp: {
    name: 'modalSlideUp',
    keyframes: {
      from: { opacity: 0, transform: 'translateY(20px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
    duration: '0.5s',
    timing: 'cubic-bezier(0.16, 1, 0.3, 1)',
  },
};

// ============================================
// TRANSITION VARIABLES (5 + extras)
// ============================================

export const transitions = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
  smooth: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
  bounce: '600ms cubic-bezier(0.16, 1, 0.3, 1)',
};

// ============================================
// HOVER EFFECTS (18 components)
// Transform, duration, and additional effects
// ============================================

export const hover = {
  header: {
    transform: 'translateY(-1px)',
    duration: transitions.smooth,
    additional: 'shadow-change',
  },

  weekTab: {
    transform: 'translateY(-2px)',
    duration: transitions.smooth,
    additional: 'border-color',
  },

  weekTabShine: {
    transform: 'translateX(100%)',
    duration: '0.6s',
    additional: 'shine-effect',
  },

  metricCard: {
    transform: 'translateY(-3px)',
    duration: transitions.smooth,
    additional: 'shadow-accent',
  },

  metricIcon: {
    transform: 'scale(1.05)',
    duration: transitions.smooth,
    additional: 'opacity-change',
  },

  metricValue: {
    transform: 'scale(1.02)',
    duration: transitions.smooth,
    additional: 'color-change',
  },

  restaurantCard: {
    transform: 'translateY(-5px) scale(1.01)',
    duration: transitions.smooth,
    additional: 'glow-shadow',
  },

  restaurantHeaderShine: {
    animation: 'slideGloss 1s ease-in-out',
    trigger: 'on-hover',
  },

  restaurantMetric: {
    transform: 'translateY(-1px)',
    duration: transitions.fast,
    additional: 'brighter-bg',
  },

  modalClose: {
    transform: 'rotate(90deg)',
    duration: '0.3s',
    additional: 'spin-effect',
  },

  pnlQuadrant: {
    transform: 'translateY(-2px)',
    duration: '0.3s',
    additional: 'border-accent',
  },

  dayCard: {
    transform: 'none',  // Only shadow
    duration: transitions.base,
    additional: 'shadow-change',
  },

  autoClockoutRow: {
    transform: 'none',  // Only background
    duration: '0.2s',
    additional: 'background',
  },

  tableRow: {
    transform: 'none',  // Only background
    duration: transitions.fast,
    additional: 'background',
  },

  button: {
    transform: 'translateY(-1px)',
    duration: transitions.fast,
    additional: 'shadow',
  },
};

// ============================================
// STAGGER DELAYS (2 patterns)
// For sequential animations
// ============================================

export const stagger = {
  metricCards: {
    count: 6,
    interval: '0.05s',
    delays: ['0.05s', '0.1s', '0.15s', '0.2s', '0.25s', '0.3s'],
  },

  restaurantCards: {
    count: 6,
    interval: '0.1s',
    delays: ['0.1s', '0.2s', '0.3s', '0.4s', '0.5s', '0.6s'],
  },
};

// ============================================
// REDUCED MOTION PREFERENCES
// Accessibility fallbacks
// ============================================

export const reducedMotion = {
  enabled: true,
  fallbacks: {
    bodyShimmer: 'disable',
    headerRotation: 'disable',
    titleAnimations: 'instant',
    weekTabTransforms: 'disable',
    panelAnimations: 'simplified',
    metricAnimations: 'disable',
    cardAnimations: 'disable',
  },
  mediaQuery: '@media (prefers-reduced-motion: reduce)',
};

// ============================================
// PERFORMANCE HINTS
// GPU acceleration and optimizations
// ============================================

export const performance = {
  willChange: {
    transform: 'will-change: transform',
    opacity: 'will-change: opacity',
    transformOpacity: 'will-change: transform, opacity',
  },

  gpuAcceleration: {
    translateZ: 'transform: translateZ(0)',
    backfaceVisibility: 'backface-visibility: hidden',
    perspective: 'perspective: 1000px',
  },

  isolation: {
    isolate: 'isolation: isolate',
  },
};

// ============================================
// CSS VARIABLES (for injection into :root)
// ============================================

export const cssVariables = {
  '--transition-fast': transitions.fast,
  '--transition-base': transitions.base,
  '--transition-smooth': transitions.smooth,
  '--transition-slow': transitions.slow,
  '--transition-bounce': transitions.bounce,
};

// ============================================
// TAILWIND ANIMATION CONFIG
// ============================================

export const tailwindAnimations = {
  keyframes: Object.entries(keyframes).reduce((acc, [key, anim]) => {
    acc[anim.name] = anim.keyframes;
    return acc;
  }, {}),

  animation: Object.entries(keyframes).reduce((acc, [key, anim]) => {
    const duration = anim.duration || '1s';
    const timing = anim.timing || 'ease';
    const iteration = anim.iteration || '1';
    acc[key] = `${anim.name} ${duration} ${timing} ${iteration}`;
    return acc;
  }, {}),

  transitionDuration: {
    fast: '150ms',
    DEFAULT: '200ms',
    base: '200ms',
    smooth: '300ms',
    slow: '500ms',
    bounce: '600ms',
  },

  transitionTimingFunction: {
    'ease-custom': 'cubic-bezier(0.4, 0, 0.2, 1)',
    'bounce': 'cubic-bezier(0.16, 1, 0.3, 1)',
  },
};

// ============================================
// EXPORT
// ============================================

export default {
  keyframes,
  transitions,
  hover,
  stagger,
  reducedMotion,
  performance,
  cssVariables,
  tailwindAnimations,

  // Metadata
  totalConfigs: 48,
  auditSource: 'DashboardV3_Audit_538_Configs',
  lastUpdated: '2025-11-01',
  transitionSource: conflicts.transitionSource, // 'css-vars'
};
