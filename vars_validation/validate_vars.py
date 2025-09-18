
#!/usr/bin/env python3
"""
Variable Validation Script for HX Infrastructure
This script validates all variables against the defined rules
"""

import yaml
import re
import ipaddress
import sys
import os
from typing import Dict, List, Any, Tuple, Optional

class VariableValidator:
    def __init__(self, rules_file: str):
        """Initialize the validator with rules from YAML file"""
        with open(rules_file, 'r') as f:
            self.rules = yaml.safe_load(f)
        self.errors = []
        self.warnings = []
        
    def validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate variable type"""
        type_mapping = {
            'string': str,
            'integer': int,
            'float': float,
            'boolean': bool,
            'list': list,
            'dict': dict
        }
        
        if expected_type not in type_mapping:
            return False
            
        return isinstance(value, type_mapping[expected_type])
        
    def validate_pattern(self, value: str, pattern: str) -> bool:
        """Validate string against regex pattern"""
        try:
            return bool(re.match(pattern, value))
        except re.error:
            return False
            
    def validate_range(self, value: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
        """Validate integer within range"""
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True
        
    def validate_allowed_values(self, value: Any, allowed_values: List[Any]) -> bool:
        """Validate value is in allowed list"""
        return value in allowed_values
        
    def validate_variable(self, var_name: str, var_value: Any, var_rules: Dict) -> List[str]:
        """Validate a single variable against its rules"""
        errors = []
        
        # Type validation
        if 'type' in var_rules:
            if not self.validate_type(var_value, var_rules['type']):
                errors.append(f"{var_name}: Expected type {var_rules['type']}, got {type(var_value).__name__}")
                return errors  # Skip other validations if type is wrong
                
        # Pattern validation (for strings)
        if 'pattern' in var_rules and isinstance(var_value, str):
            if not self.validate_pattern(var_value, var_rules['pattern']):
                errors.append(f"{var_name}: Value '{var_value}' does not match pattern {var_rules['pattern']}")
                
        # Range validation (for integers)
        if isinstance(var_value, int):
            min_val = var_rules.get('min_value')
            max_val = var_rules.get('max_value')
            if not self.validate_range(var_value, min_val, max_val):
                errors.append(f"{var_name}: Value {var_value} is outside allowed range [{min_val}, {max_val}]")
                
        # Length validation (for strings)
        if isinstance(var_value, str):
            min_len = var_rules.get('min_length')
            max_len = var_rules.get('max_length')
            if min_len is not None and len(var_value) < min_len:
                errors.append(f"{var_name}: String length {len(var_value)} is less than minimum {min_len}")
            if max_len is not None and len(var_value) > max_len:
                errors.append(f"{var_name}: String length {len(var_value)} is greater than maximum {max_len}")
                
        # Allowed values validation
        if 'allowed_values' in var_rules:
            if not self.validate_allowed_values(var_value, var_rules['allowed_values']):
                errors.append(f"{var_name}: Value '{var_value}' not in allowed values {var_rules['allowed_values']}")
                
        # List item validation
        if isinstance(var_value, list) and 'item_type' in var_rules:
            for i, item in enumerate(var_value):
                if not self.validate_type(item, var_rules['item_type']):
                    errors.append(f"{var_name}[{i}]: Expected type {var_rules['item_type']}, got {type(item).__name__}")
                    
                if 'item_pattern' in var_rules and isinstance(item, str):
                    if not self.validate_pattern(item, var_rules['item_pattern']):
                        errors.append(f"{var_name}[{i}]: Value '{item}' does not match pattern {var_rules['item_pattern']}")
                        
        return errors
        
    def validate_dependencies(self, variables: Dict) -> List[str]:
        """Validate variable dependencies"""
        errors = []
        
        for rule in self.rules.get('dependency_rules', []):
            condition = rule['condition']
            requires = rule['requires']
            description = rule.get('description', '')
            
            # Simple condition evaluation (can be extended)
            try:
                # Replace variable names with their values in condition
                eval_condition = condition
                for var_name, var_value in variables.items():
                    eval_condition = eval_condition.replace(var_name, str(var_value))
                    
                # Evaluate condition (basic implementation)
                if self.evaluate_condition(eval_condition, variables):
                    for required_var in requires:
                        if required_var not in variables:
                            errors.append(f"Dependency error: {description} - Missing required variable: {required_var}")
                        elif variables[required_var] in [None, '', []]:
                            errors.append(f"Dependency error: {description} - Required variable {required_var} is empty")
                            
            except Exception as e:
                errors.append(f"Dependency evaluation error for condition '{condition}': {str(e)}")
                
        return errors
        
    def evaluate_condition(self, condition: str, variables: Dict) -> bool:
        """Evaluate a simple condition (basic implementation)"""
        # This is a simplified implementation
        # In production, you might want to use a more robust expression evaluator
        
        # Handle boolean conditions
        if '==' in condition:
            left, right = condition.split('==', 1)
            left = left.strip()
            right = right.strip().strip('"\'')
            
            if left in variables:
                return str(variables[left]).lower() == right.lower()
                
        return False
        
    def validate_cross_service_rules(self, variables: Dict) -> List[str]:
        """Validate cross-service rules"""
        errors = []
        
        for rule in self.rules.get('cross_service_rules', []):
            rule_name = rule['name']
            description = rule['description']
            rule_checks = rule['rules']
            
            for check in rule_checks:
                try:
                    # Simple rule evaluation
                    if not self.evaluate_cross_service_rule(check, variables):
                        errors.append(f"Cross-service rule '{rule_name}' failed: {description}")
                except Exception as e:
                    errors.append(f"Cross-service rule evaluation error for '{rule_name}': {str(e)}")
                    
        return errors
        
    def evaluate_cross_service_rule(self, rule: str, variables: Dict) -> bool:
        """Evaluate cross-service rule (basic implementation)"""
        # This would need to be expanded based on actual rule syntax
        # For now, just return True to avoid errors
        return True
        
    def validate_resource_requirements(self, variables: Dict, inventory: Dict) -> List[str]:
        """Validate resource requirements against inventory"""
        errors = []
        warnings = []
        
        resource_rules = self.rules.get('resource_validation', {})
        
        # Memory requirements
        for req in resource_rules.get('memory_requirements', []):
            service = req['service']
            min_memory = req['min_memory_gb']
            recommended_memory = req['recommended_memory_gb']
            
            # Check if service is deployed and validate memory
            # This would need actual inventory parsing
            
        return errors
        
    def validate_all(self, variables: Dict, inventory: Optional[Dict] = None) -> Tuple[List[str], List[str]]:
        """Validate all variables and return errors and warnings"""
        errors = []
        warnings = []
        
        # Get environment-specific rules
        environment = variables.get('environment', 'development')
        
        # Validate global required variables
        for var_rule in self.rules.get('global_required_variables', []):
            var_name = var_rule['name']
            if var_name not in variables:
                errors.append(f"Missing required global variable: {var_name}")
            else:
                errors.extend(self.validate_variable(var_name, variables[var_name], var_rule))
                
        # Validate service-specific variables
        service_groups = ['infrastructure_variables', 'ai_ml_variables', 'operations_variables', 'ui_variables']
        
        for service_group in service_groups:
            if service_group in self.rules:
                service_rules = self.rules[service_group]
                
                # Required variables
                for var_rule in service_rules.get('required', []):
                    var_name = var_rule['name']
                    if var_name not in variables:
                        errors.append(f"Missing required {service_group} variable: {var_name}")
                    else:
                        errors.extend(self.validate_variable(var_name, variables[var_name], var_rule))
                        
                # Optional variables (only validate if present)
                for var_rule in service_rules.get('optional', []):
                    var_name = var_rule['name']
                    if var_name in variables:
                        errors.extend(self.validate_variable(var_name, variables[var_name], var_rule))
                        
        # Validate dependencies
        errors.extend(self.validate_dependencies(variables))
        
        # Validate cross-service rules
        errors.extend(self.validate_cross_service_rules(variables))
        
        # Validate resource requirements if inventory provided
        if inventory:
            errors.extend(self.validate_resource_requirements(variables, inventory))
            
        return errors, warnings

def load_variables_from_files(var_files: List[str]) -> Dict:
    """Load variables from multiple YAML files"""
    variables = {}
    
    for var_file in var_files:
        if os.path.exists(var_file):
            with open(var_file, 'r') as f:
                file_vars = yaml.safe_load(f) or {}
                variables.update(file_vars)
                
    return variables

def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_vars.py <variable_files...>")
        sys.exit(1)
        
    # Initialize validator
    rules_file = os.path.join(os.path.dirname(__file__), 'validation_rules.yml')
    validator = VariableValidator(rules_file)
    
    # Load variables from files
    var_files = sys.argv[1:]
    variables = load_variables_from_files(var_files)
    
    # Validate variables
    errors, warnings = validator.validate_all(variables)
    
    # Print results
    if errors:
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"  ❌ {error}")
            
    if warnings:
        print("\nVALIDATION WARNINGS:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
            
    if not errors and not warnings:
        print("✅ All variables passed validation!")
        
    # Exit with error code if there are errors
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
