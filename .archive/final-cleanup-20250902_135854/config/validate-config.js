#!/usr/bin/env node

/**
 * Configuration Validation Script
 * Validates app configuration files for correctness and completeness
 */

const fs = require('fs');
const path = require('path');

const REQUIRED_FIELDS = {
  'app': ['name', 'version', 'environment'],
  'backend': ['host', 'port', 'protocol'],
  'frontend': [],
  'features': []
};

const VALID_ENVIRONMENTS = ['development', 'production', 'test'];
const VALID_PROTOCOLS = ['http', 'https'];
const VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];

class ConfigValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
  }
  
  loadConfig(configPath) {
    if (!fs.existsSync(configPath)) {
      throw new Error(`Config file not found: ${configPath}`);
    }
    
    const content = fs.readFileSync(configPath, 'utf8');
    try {
      return JSON.parse(content);
    } catch (e) {
      throw new Error(`Invalid JSON in ${configPath}: ${e.message}`);
    }
  }
  
  validateStructure(config, configName) {
    // Check required top-level fields
    for (const [section, fields] of Object.entries(REQUIRED_FIELDS)) {
      if (!config[section]) {
        this.errors.push(`${configName}: Missing required section '${section}'`);
        continue;
      }
      
      for (const field of fields) {
        if (!config[section][field]) {
          this.errors.push(`${configName}: Missing required field '${section}.${field}'`);
        }
      }
    }
  }
  
  validateValues(config, configName) {
    // Validate environment
    if (config.app?.environment && !VALID_ENVIRONMENTS.includes(config.app.environment)) {
      this.errors.push(`${configName}: Invalid environment '${config.app.environment}'. Must be one of: ${VALID_ENVIRONMENTS.join(', ')}`);
    }
    
    // Validate backend configuration
    if (config.backend) {
      // Validate port
      if (config.backend.port) {
        const port = parseInt(config.backend.port);
        if (isNaN(port) || port < 1 || port > 65535) {
          this.errors.push(`${configName}: Invalid port '${config.backend.port}'. Must be between 1 and 65535`);
        }
      }
      
      // Validate protocol
      if (config.backend.protocol && !VALID_PROTOCOLS.includes(config.backend.protocol)) {
        this.errors.push(`${configName}: Invalid protocol '${config.backend.protocol}'. Must be one of: ${VALID_PROTOCOLS.join(', ')}`);
      }
      
      // Validate host
      if (config.backend.host) {
        const validHostPattern = /^(localhost|127\.0\.0\.1|0\.0\.0\.0|[\w\.-]+)$/;
        if (!validHostPattern.test(config.backend.host)) {
          this.warnings.push(`${configName}: Unusual host value '${config.backend.host}'`);
        }
      }
    }
    
    // Validate logging
    if (config.logging?.level && !VALID_LOG_LEVELS.includes(config.logging.level)) {
      this.warnings.push(`${configName}: Invalid log level '${config.logging.level}'. Should be one of: ${VALID_LOG_LEVELS.join(', ')}`);
    }
    
    // Check for environment variables
    this.checkEnvironmentVariables(config, configName);
  }
  
  checkEnvironmentVariables(config, configName, path = '') {
    for (const [key, value] of Object.entries(config)) {
      const currentPath = path ? `${path}.${key}` : key;
      
      if (typeof value === 'string' && value.startsWith('${') && value.endsWith('}')) {
        const envVar = value.slice(2, -1);
        if (!process.env[envVar]) {
          this.warnings.push(`${configName}: Environment variable '${envVar}' at '${currentPath}' is not set`);
        }
      } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        this.checkEnvironmentVariables(value, configName, currentPath);
      }
    }
  }
  
  validateCompatibility(baseConfig, envConfig, envName) {
    // Check that env config doesn't introduce new required fields
    const checkCompatibility = (base, env, path = '') => {
      for (const [key, value] of Object.entries(env)) {
        const currentPath = path ? `${path}.${key}` : key;
        
        if (!(key in base) && typeof value === 'object' && value !== null) {
          this.warnings.push(`${envName}: Introduces new section '${currentPath}' not in base config`);
        }
      }
    };
    
    checkCompatibility(baseConfig, envConfig);
  }
  
  validateAll() {
    const configDir = path.join(__dirname);
    
    // Load and validate base config
    console.log('Validating base configuration...');
    const baseConfigPath = path.join(configDir, 'app.config.json');
    const baseConfig = this.loadConfig(baseConfigPath);
    this.validateStructure(baseConfig, 'app.config.json');
    this.validateValues(baseConfig, 'app.config.json');
    
    // Load and validate environment configs
    const envConfigs = ['development', 'production'];
    for (const env of envConfigs) {
      const envConfigPath = path.join(configDir, `app.config.${env}.json`);
      if (fs.existsSync(envConfigPath)) {
        console.log(`Validating ${env} configuration...`);
        const envConfig = this.loadConfig(envConfigPath);
        this.validateValues(envConfig, `app.config.${env}.json`);
        this.validateCompatibility(baseConfig, envConfig, `app.config.${env}.json`);
      }
    }
    
    // Report results
    console.log('\n' + '='.repeat(50));
    
    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log('✅ All configuration files are valid!');
      return true;
    }
    
    if (this.errors.length > 0) {
      console.log(`\n❌ Found ${this.errors.length} error(s):`);
      this.errors.forEach(error => console.log(`  - ${error}`));
    }
    
    if (this.warnings.length > 0) {
      console.log(`\n⚠️  Found ${this.warnings.length} warning(s):`);
      this.warnings.forEach(warning => console.log(`  - ${warning}`));
    }
    
    return this.errors.length === 0;
  }
}

// Run validation if called directly
if (require.main === module) {
  const validator = new ConfigValidator();
  const isValid = validator.validateAll();
  process.exit(isValid ? 0 : 1);
}

module.exports = ConfigValidator;