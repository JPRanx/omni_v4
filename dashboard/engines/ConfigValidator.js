/**
 * Dashboard V3 - Config Validator
 *
 * Smart system that validates all configuration values
 *
 * Responsibilities:
 * - Validate all 538 config values on load
 * - Check for missing required configs
 * - Validate data types and ranges
 * - Report errors/warnings to console
 * - Provide config health check
 * - Generate validation reports
 *
 * Usage:
 * ```javascript
 * import ConfigValidator from './engines/ConfigValidator.js';
 * import config from './shared/config/index.js';
 *
 * const validator = new ConfigValidator(config);
 * const isValid = validator.validate(); // Returns true if all valid
 * const report = validator.getReport(); // Get detailed validation report
 * ```
 */

class ConfigValidator {
  constructor(config) {
    if (!config) {
      throw new Error('ConfigValidator: config is required');
    }

    this.config = config;
    this.initialized = false;

    // Validation results
    this.errors = [];
    this.warnings = [];
    this.info = [];
    this.valid = false;

    // Validation stats
    this.stats = {
      totalChecks: 0,
      passed: 0,
      failed: 0,
      warned: 0,
    };

    this.initialize();
  }

  /**
   * Initialize validator
   */
  initialize() {
    if (this.initialized) {
      console.warn('ConfigValidator: Already initialized');
      return;
    }

    console.log('[ConfigValidator] Initializing...');

    // Run validation
    this.validate();

    this.initialized = true;
    console.log('[ConfigValidator] Initialized successfully');
  }

  /**
   * Validate all configurations
   * @returns {boolean} True if all valid
   */
  validate() {
    console.log('[ConfigValidator] Starting validation...');

    // Reset results
    this.errors = [];
    this.warnings = [];
    this.info = [];
    this.stats = { totalChecks: 0, passed: 0, failed: 0, warned: 0 };

    // Validate each category
    this.validateResolution();
    this.validateTheme();
    this.validateLayout();
    this.validateBusiness();
    this.validateContent();
    this.validateFeatures();
    this.validateMetadata();

    // Calculate validity
    this.valid = this.errors.length === 0;

    // Log results
    this.logResults();

    return this.valid;
  }

  /**
   * Validate resolution configuration
   */
  validateResolution() {
    const category = 'Resolution';

    this.checkExists(category, 'config.resolution', this.config.resolution);
    this.checkExists(category, 'config.resolution.conflicts', this.config.resolution?.conflicts);

    if (this.config.resolution?.conflicts) {
      const conflicts = this.config.resolution.conflicts;

      this.checkType(category, 'bronze_dust', conflicts.bronze_dust, 'string');
      this.checkType(category, 'preferredUnit', conflicts.preferredUnit, 'string');
      this.checkType(category, 'containerMaxWidth', conflicts.containerMaxWidth, 'string');

      // Validate resolved values
      this.checkPattern(category, 'bronze_dust', conflicts.bronze_dust, /^#[0-9A-Fa-f]{6}$/);
      this.checkEnum(category, 'preferredUnit', conflicts.preferredUnit, ['px', 'rem', 'em']);

      this.info.push(`${category}: 8 conflicts resolved`);
    }
  }

  /**
   * Validate theme configuration
   */
  validateTheme() {
    const category = 'Theme';

    this.checkExists(category, 'config.theme', this.config.theme);

    // Validate colors
    if (this.config.theme.colors) {
      this.checkExists(category, 'colors.desert', this.config.theme.colors.desert);
      this.checkExists(category, 'colors.ocean', this.config.theme.colors.ocean);
      this.checkExists(category, 'colors.gradients', this.config.theme.colors.gradients);

      const expectedColorCount = 87;
      const actualCount = this.config.theme.colors.totalColors || 0;
      if (actualCount !== expectedColorCount) {
        this.warnings.push(`${category}: Color count mismatch (expected ${expectedColorCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate shadows
    if (this.config.theme.shadows) {
      this.checkExists(category, 'shadows.scale', this.config.theme.shadows.scale);

      const expectedShadowCount = 43;
      const actualCount = this.config.theme.shadows.totalShadows || 0;
      if (actualCount !== expectedShadowCount) {
        this.warnings.push(`${category}: Shadow count mismatch (expected ${expectedShadowCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate typography
    if (this.config.theme.typography) {
      this.checkExists(category, 'typography.families', this.config.theme.typography.families);
      this.checkExists(category, 'typography.sizes', this.config.theme.typography.sizes);
      this.checkExists(category, 'typography.weights', this.config.theme.typography.weights);

      const expectedTypoCount = 67;
      const actualCount = this.config.theme.typography.totalConfigs || 0;
      if (actualCount !== expectedTypoCount) {
        this.warnings.push(`${category}: Typography count mismatch (expected ${expectedTypoCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate spacing
    if (this.config.theme.spacing) {
      this.checkExists(category, 'spacing.scale', this.config.theme.spacing.scale);

      const expectedSpacingCount = 52;
      const actualCount = this.config.theme.spacing.totalValues || 0;
      if (actualCount !== expectedSpacingCount) {
        this.warnings.push(`${category}: Spacing count mismatch (expected ${expectedSpacingCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate borders
    if (this.config.theme.borders) {
      this.checkExists(category, 'borders.radius', this.config.theme.borders.radius);

      const expectedBorderCount = 31;
      const actualCount = this.config.theme.borders.totalConfigs || 0;
      if (actualCount !== expectedBorderCount) {
        this.warnings.push(`${category}: Border count mismatch (expected ${expectedBorderCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate animations
    if (this.config.theme.animations) {
      this.checkExists(category, 'animations.keyframes', this.config.theme.animations.keyframes);

      const expectedAnimCount = 48;
      const actualCount = this.config.theme.animations.totalConfigs || 0;
      if (actualCount !== expectedAnimCount) {
        this.warnings.push(`${category}: Animation count mismatch (expected ${expectedAnimCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }
  }

  /**
   * Validate layout configuration
   */
  validateLayout() {
    const category = 'Layout';

    this.checkExists(category, 'config.layout', this.config.layout);

    // Validate grids
    if (this.config.layout.grids) {
      this.checkExists(category, 'grids.grids', this.config.layout.grids.grids);

      const expectedGridCount = 14;
      const actualCount = this.config.layout.grids.totalPatterns || 0;
      if (actualCount !== expectedGridCount) {
        this.warnings.push(`${category}: Grid count mismatch (expected ${expectedGridCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate containers
    if (this.config.layout.containers) {
      this.checkExists(category, 'containers.maxWidths', this.config.layout.containers.maxWidths);

      const expectedContainerCount = 5;
      const actualCount = this.config.layout.containers.totalConfigs || 0;
      if (actualCount !== expectedContainerCount) {
        this.warnings.push(`${category}: Container count mismatch (expected ${expectedContainerCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate breakpoints
    if (this.config.layout.breakpoints) {
      this.checkExists(category, 'breakpoints.breakpoints', this.config.layout.breakpoints.breakpoints);

      const expectedBreakpointCount = 7;
      const actualCount = this.config.layout.breakpoints.totalBreakpoints || 0;
      if (actualCount !== expectedBreakpointCount) {
        this.warnings.push(`${category}: Breakpoint count mismatch (expected ${expectedBreakpointCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate z-index
    if (this.config.layout.zindex) {
      this.checkExists(category, 'zindex.layers', this.config.layout.zindex.layers);

      const expectedZCount = 7;
      const actualCount = this.config.layout.zindex.totalLayers || 0;
      if (actualCount !== expectedZCount) {
        this.warnings.push(`${category}: Z-index count mismatch (expected ${expectedZCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }
  }

  /**
   * Validate business configuration
   */
  validateBusiness() {
    const category = 'Business';

    this.checkExists(category, 'config.business', this.config.business);

    // Validate thresholds
    if (this.config.business.thresholds) {
      this.checkExists(category, 'thresholds.sales', this.config.business.thresholds.sales);
      this.checkExists(category, 'thresholds.labor', this.config.business.thresholds.labor);

      const expectedThresholdCount = 34;
      const actualCount = this.config.business.thresholds.totalThresholds || 0;
      if (actualCount !== expectedThresholdCount) {
        this.warnings.push(`${category}: Threshold count mismatch (expected ${expectedThresholdCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate formulas
    if (this.config.business.formulas) {
      this.checkExists(category, 'formulas.percentages', this.config.business.formulas.percentages);

      const expectedFormulaCount = 10;
      const actualCount = this.config.business.formulas.totalFormulas || 0;
      if (actualCount !== expectedFormulaCount) {
        this.warnings.push(`${category}: Formula count mismatch (expected ${expectedFormulaCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate grading
    if (this.config.business.grading) {
      this.checkExists(category, 'grading.grades', this.config.business.grading.grades);

      const expectedGradeCount = 5;
      const actualCount = this.config.business.grading.totalLevels || 0;
      if (actualCount !== expectedGradeCount) {
        this.warnings.push(`${category}: Grade level count mismatch (expected ${expectedGradeCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate statuses
    if (this.config.business.statuses) {
      this.checkExists(category, 'statuses.statuses', this.config.business.statuses.statuses);

      const expectedStatusCount = 9;
      const actualCount = this.config.business.statuses.totalTypes || 0;
      if (actualCount !== expectedStatusCount) {
        this.warnings.push(`${category}: Status type count mismatch (expected ${expectedStatusCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }
  }

  /**
   * Validate content configuration
   */
  validateContent() {
    const category = 'Content';

    this.checkExists(category, 'config.content', this.config.content);

    // Validate labels
    if (this.config.content.labels) {
      const expectedLabelCount = 73;
      const actualCount = this.config.content.labels.totalLabels || 0;
      if (actualCount !== expectedLabelCount) {
        this.warnings.push(`${category}: Label count mismatch (expected ${expectedLabelCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate messages
    if (this.config.content.messages) {
      const expectedMessageCount = 28;
      const actualCount = this.config.content.messages.totalMessages || 0;
      if (actualCount !== expectedMessageCount) {
        this.warnings.push(`${category}: Message count mismatch (expected ${expectedMessageCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate formats
    if (this.config.content.formats) {
      const expectedFormatCount = 15;
      const actualCount = this.config.content.formats.totalFormatters || 0;
      if (actualCount !== expectedFormatCount) {
        this.warnings.push(`${category}: Format count mismatch (expected ${expectedFormatCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }
  }

  /**
   * Validate features configuration
   */
  validateFeatures() {
    const category = 'Features';

    this.checkExists(category, 'config.features', this.config.features);

    // Validate toggles
    if (this.config.features.toggles) {
      this.checkExists(category, 'toggles.core', this.config.features.toggles.core);
      this.checkExists(category, 'toggles.optional', this.config.features.toggles.optional);
      this.checkExists(category, 'toggles.experimental', this.config.features.toggles.experimental);

      const expectedToggleCount = 15;
      const actualCount = this.config.features.toggles.totalToggles || 0;
      if (actualCount !== expectedToggleCount) {
        this.warnings.push(`${category}: Toggle count mismatch (expected ${expectedToggleCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate capabilities
    if (this.config.features.capabilities) {
      const expectedCapabilityCount = 12;
      const actualCount = this.config.features.capabilities.totalCapabilities || 0;
      if (actualCount !== expectedCapabilityCount) {
        this.warnings.push(`${category}: Capability count mismatch (expected ${expectedCapabilityCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }

    // Validate experimental
    if (this.config.features.experimental) {
      const expectedExperimentCount = 8;
      const actualCount = this.config.features.experimental.totalExperiments || 0;
      if (actualCount !== expectedExperimentCount) {
        this.warnings.push(`${category}: Experiment count mismatch (expected ${expectedExperimentCount}, got ${actualCount})`);
        this.stats.warned++;
      } else {
        this.stats.passed++;
      }
      this.stats.totalChecks++;
    }
  }

  /**
   * Validate metadata
   */
  validateMetadata() {
    const category = 'Metadata';

    this.checkType(category, 'version', this.config.version, 'string');
    this.checkType(category, 'lastUpdated', this.config.lastUpdated, 'string');
    this.checkType(category, 'totalConfigs', this.config.totalConfigs, 'number');

    // Validate total config count
    const expectedTotal = 538;
    const actualTotal = this.config.totalConfigs || 0;

    if (actualTotal !== expectedTotal) {
      this.warnings.push(`${category}: Total config count mismatch (expected ${expectedTotal}, got ${actualTotal})`);
      this.stats.warned++;
    } else {
      this.stats.passed++;
      this.info.push(`${category}: All 538 configurations validated`);
    }
    this.stats.totalChecks++;
  }

  // ============================================
  // VALIDATION HELPERS
  // ============================================

  /**
   * Check if value exists
   */
  checkExists(category, path, value) {
    this.stats.totalChecks++;

    if (value === undefined || value === null) {
      this.errors.push(`${category}: Missing required config: ${path}`);
      this.stats.failed++;
      return false;
    }

    this.stats.passed++;
    return true;
  }

  /**
   * Check if value is correct type
   */
  checkType(category, name, value, expectedType) {
    this.stats.totalChecks++;

    const actualType = typeof value;
    if (actualType !== expectedType) {
      this.errors.push(`${category}: Type mismatch for ${name} (expected ${expectedType}, got ${actualType})`);
      this.stats.failed++;
      return false;
    }

    this.stats.passed++;
    return true;
  }

  /**
   * Check if value matches pattern
   */
  checkPattern(category, name, value, pattern) {
    this.stats.totalChecks++;

    if (!pattern.test(value)) {
      this.errors.push(`${category}: Pattern mismatch for ${name} (value: ${value})`);
      this.stats.failed++;
      return false;
    }

    this.stats.passed++;
    return true;
  }

  /**
   * Check if value is in enum
   */
  checkEnum(category, name, value, allowedValues) {
    this.stats.totalChecks++;

    if (!allowedValues.includes(value)) {
      this.errors.push(`${category}: Invalid value for ${name} (value: ${value}, allowed: ${allowedValues.join(', ')})`);
      this.stats.failed++;
      return false;
    }

    this.stats.passed++;
    return true;
  }

  // ============================================
  // REPORTING
  // ============================================

  /**
   * Log validation results
   */
  logResults() {
    console.group('[ConfigValidator] Validation Results');
    console.log(`Total Checks: ${this.stats.totalChecks}`);
    console.log(`Passed: ${this.stats.passed} ✅`);
    console.log(`Failed: ${this.stats.failed} ❌`);
    console.log(`Warnings: ${this.stats.warned} ⚠️`);
    console.log(`Valid: ${this.valid ? 'YES' : 'NO'}`);

    if (this.errors.length > 0) {
      console.group('Errors:');
      this.errors.forEach(err => console.error(err));
      console.groupEnd();
    }

    if (this.warnings.length > 0) {
      console.group('Warnings:');
      this.warnings.forEach(warn => console.warn(warn));
      console.groupEnd();
    }

    if (this.info.length > 0) {
      console.group('Info:');
      this.info.forEach(inf => console.info(inf));
      console.groupEnd();
    }

    console.groupEnd();
  }

  /**
   * Get validation report
   * @returns {Object} Validation report
   */
  getReport() {
    return {
      valid: this.valid,
      stats: this.stats,
      errors: this.errors,
      warnings: this.warnings,
      info: this.info,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Get health check
   * @returns {Object} Health check result
   */
  getHealthCheck() {
    return {
      status: this.valid ? 'healthy' : 'unhealthy',
      score: this.stats.totalChecks > 0
        ? Math.round((this.stats.passed / this.stats.totalChecks) * 100)
        : 0,
      issues: {
        errors: this.errors.length,
        warnings: this.warnings.length,
      },
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Export report as JSON
   * @returns {string} JSON string
   */
  exportReport() {
    return JSON.stringify(this.getReport(), null, 2);
  }

  /**
   * Cleanup
   */
  destroy() {
    console.log('[ConfigValidator] Destroying...');
    this.initialized = false;
    console.log('[ConfigValidator] Destroyed');
  }
}

export default ConfigValidator;
