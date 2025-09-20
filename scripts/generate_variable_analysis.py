
#!/usr/bin/env python3
"""
Variable Analysis Generator - Phase 3 Day 1
Comprehensive variable mapping and consistency analysis
"""

import os
import yaml
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

class VariableAnalyzer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.variables = defaultdict(list)
        self.variable_sources = defaultdict(set)
        self.naming_issues = []
        self.consistency_issues = []
        
    def scan_yaml_files(self):
        """Scan all YAML files for variable definitions"""
        yaml_files = []
        
        # Scan common directories
        for directory in ['group_vars', 'host_vars', 'vars', 'roles']:
            dir_path = self.base_path / directory
            if dir_path.exists():
                yaml_files.extend(dir_path.rglob('*.yml'))
                yaml_files.extend(dir_path.rglob('*.yaml'))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        self.extract_variables(content, str(yaml_file.relative_to(self.base_path)))
            except Exception as e:
                print(f"Error processing {yaml_file}: {e}")
    
    def extract_variables(self, data, source_file):
        """Extract variables from YAML data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(key, str) and not key.startswith('ansible_'):
                    self.variables[key].append({
                        'value': value,
                        'source': source_file,
                        'type': type(value).__name__
                    })
                    self.variable_sources[key].add(source_file)
                
                # Recursively check nested dictionaries
                if isinstance(value, dict):
                    self.extract_nested_variables(value, source_file, key)
    
    def extract_nested_variables(self, data, source_file, parent_key):
        """Extract nested variables"""
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}"
                if isinstance(key, str):
                    self.variables[full_key].append({
                        'value': value,
                        'source': source_file,
                        'type': type(value).__name__,
                        'parent': parent_key
                    })
                    self.variable_sources[full_key].add(source_file)
                
                if isinstance(value, dict):
                    self.extract_nested_variables(value, source_file, full_key)
    
    def analyze_naming_conventions(self):
        """Analyze variable naming conventions"""
        naming_patterns = {
            'snake_case': re.compile(r'^[a-z][a-z0-9_]*$'),
            'camelCase': re.compile(r'^[a-z][a-zA-Z0-9]*$'),
            'PascalCase': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
            'kebab-case': re.compile(r'^[a-z][a-z0-9-]*$')
        }
        
        pattern_counts = Counter()
        
        for var_name in self.variables.keys():
            matched_pattern = None
            for pattern_name, pattern in naming_patterns.items():
                if pattern.match(var_name):
                    pattern_counts[pattern_name] += 1
                    matched_pattern = pattern_name
                    break
            
            if not matched_pattern:
                self.naming_issues.append({
                    'variable': var_name,
                    'issue': 'Does not match any standard naming convention',
                    'sources': list(self.variable_sources[var_name])
                })
        
        return pattern_counts
    
    def analyze_consistency(self):
        """Analyze variable consistency across files"""
        for var_name, occurrences in self.variables.items():
            if len(occurrences) > 1:
                # Check for type consistency
                types = set(occ['type'] for occ in occurrences)
                if len(types) > 1:
                    self.consistency_issues.append({
                        'variable': var_name,
                        'issue': 'Inconsistent types',
                        'types': list(types),
                        'sources': [occ['source'] for occ in occurrences]
                    })
                
                # Check for value consistency (for simple types)
                values = []
                for occ in occurrences:
                    if occ['type'] in ['str', 'int', 'bool', 'float']:
                        values.append(occ['value'])
                
                if len(set(str(v) for v in values)) > 1:
                    self.consistency_issues.append({
                        'variable': var_name,
                        'issue': 'Inconsistent values',
                        'values': values,
                        'sources': [occ['source'] for occ in occurrences]
                    })
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        self.scan_yaml_files()
        naming_patterns = self.analyze_naming_conventions()
        self.analyze_consistency()
        
        # Generate statistics
        total_variables = len(self.variables)
        unique_variables = len(set(self.variables.keys()))
        duplicate_variables = sum(1 for v in self.variables.values() if len(v) > 1)
        
        # Categorize variables by prefix
        prefix_categories = defaultdict(list)
        for var_name in self.variables.keys():
            if '_' in var_name:
                prefix = var_name.split('_')[0]
                prefix_categories[prefix].append(var_name)
        
        report = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'base_path': str(self.base_path),
                'total_files_scanned': len(set(source for sources in self.variable_sources.values() for source in sources))
            },
            'variable_statistics': {
                'total_variables': total_variables,
                'unique_variables': unique_variables,
                'duplicate_variables': duplicate_variables,
                'naming_pattern_distribution': dict(naming_patterns)
            },
            'variable_categories': {
                'by_prefix': {k: len(v) for k, v in prefix_categories.items()},
                'top_prefixes': sorted(prefix_categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]
            },
            'consistency_analysis': {
                'naming_issues': self.naming_issues,
                'consistency_issues': self.consistency_issues,
                'total_naming_issues': len(self.naming_issues),
                'total_consistency_issues': len(self.consistency_issues)
            },
            'recommendations': self.generate_recommendations(),
            'variable_inventory': {
                var_name: {
                    'occurrences': len(occurrences),
                    'sources': list(self.variable_sources[var_name]),
                    'types': list(set(occ['type'] for occ in occurrences))
                }
                for var_name, occurrences in self.variables.items()
            }
        }
        
        return report
    
    def generate_recommendations(self):
        """Generate recommendations for improvement"""
        recommendations = []
        
        # Naming convention recommendations
        if self.naming_issues:
            recommendations.append({
                'category': 'naming_conventions',
                'priority': 'high',
                'description': f'Fix {len(self.naming_issues)} variable naming issues',
                'action': 'Standardize all variables to snake_case convention'
            })
        
        # Consistency recommendations
        if self.consistency_issues:
            recommendations.append({
                'category': 'consistency',
                'priority': 'high',
                'description': f'Resolve {len(self.consistency_issues)} consistency issues',
                'action': 'Standardize variable types and values across all files'
            })
        
        # Prefix standardization
        prefix_categories = defaultdict(list)
        for var_name in self.variables.keys():
            if '_' in var_name:
                prefix = var_name.split('_')[0]
                prefix_categories[prefix].append(var_name)
        
        if len(prefix_categories) > 10:
            recommendations.append({
                'category': 'organization',
                'priority': 'medium',
                'description': f'Too many variable prefixes ({len(prefix_categories)})',
                'action': 'Consolidate variable prefixes to improve organization'
            })
        
        return recommendations

def main():
    analyzer = VariableAnalyzer('/home/ubuntu/hx-infrastructure-ansible')
    report = analyzer.generate_report()
    
    # Save detailed report
    with open('/home/ubuntu/hx-infrastructure-ansible/docs/phase3/variable_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate markdown summary
    markdown_content = f"""# Variable Analysis Report - Phase 3 Day 1

Generated: {report['analysis_metadata']['timestamp']}

## Summary Statistics

- **Total Variables**: {report['variable_statistics']['total_variables']}
- **Unique Variables**: {report['variable_statistics']['unique_variables']}
- **Duplicate Variables**: {report['variable_statistics']['duplicate_variables']}
- **Files Scanned**: {report['analysis_metadata']['total_files_scanned']}

## Naming Pattern Distribution

"""
    
    for pattern, count in report['variable_statistics']['naming_pattern_distribution'].items():
        markdown_content += f"- **{pattern}**: {count} variables\n"
    
    markdown_content += f"""
## Issues Found

- **Naming Issues**: {report['consistency_analysis']['total_naming_issues']}
- **Consistency Issues**: {report['consistency_analysis']['total_consistency_issues']}

## Top Variable Prefixes

"""
    
    for prefix, variables in report['variable_categories']['top_prefixes'][:5]:
        markdown_content += f"- **{prefix}_**: {len(variables)} variables\n"
    
    markdown_content += """
## Recommendations

"""
    
    for rec in report['recommendations']:
        markdown_content += f"- **{rec['category'].title()}** ({rec['priority']}): {rec['description']}\n"
        markdown_content += f"  - Action: {rec['action']}\n\n"
    
    with open('/home/ubuntu/hx-infrastructure-ansible/docs/phase3/variable_analysis_summary.md', 'w') as f:
        f.write(markdown_content)
    
    print("Variable analysis completed successfully!")
    print(f"- Detailed report: docs/phase3/variable_analysis_report.json")
    print(f"- Summary: docs/phase3/variable_analysis_summary.md")
    print(f"- Total variables analyzed: {report['variable_statistics']['total_variables']}")
    print(f"- Issues found: {report['consistency_analysis']['total_naming_issues'] + report['consistency_analysis']['total_consistency_issues']}")

if __name__ == '__main__':
    main()

