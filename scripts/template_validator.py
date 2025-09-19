
#!/usr/bin/env python3
"""
Template Quality Validator for Ansible Jinja2 Templates
Implements comprehensive template analysis, security scanning, and performance optimization
"""

import os
import sys
import json
import yaml
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from jinja2 import Environment, FileSystemLoader, meta, exceptions
from jinja2schema import infer, to_json_schema
import subprocess
import hashlib
from datetime import datetime

class TemplateValidator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.env = Environment(loader=FileSystemLoader(str(self.base_path)))
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "templates": {},
            "security_issues": [],
            "performance_recommendations": [],
            "inheritance_analysis": {},
            "version": "1.0.0"
        }
        
        # Security patterns to detect
        self.security_patterns = {
            "hardcoded_secrets": [
                r'password\s*[:=]\s*["\'][^"\']+["\']',
                r'secret\s*[:=]\s*["\'][^"\']+["\']',
                r'api_key\s*[:=]\s*["\'][^"\']+["\']',
                r'token\s*[:=]\s*["\'][^"\']+["\']'
            ],
            "unsafe_operations": [
                r'\|\s*shell',
                r'\|\s*system',
                r'eval\s*\(',
                r'exec\s*\('
            ],
            "path_traversal": [
                r'\.\./\.\.',
                r'\.\.\\\.\.', 
                r'/etc/passwd',
                r'/etc/shadow'
            ]
        }
        
        # Performance anti-patterns
        self.performance_patterns = {
            "nested_loops": r'{%\s*for.*%}.*{%\s*for.*%}',
            "complex_conditionals": r'{%\s*if.*and.*or.*%}',
            "repeated_calculations": r'{{\s*.*\|\s*.*\|\s*.*\|\s*.*}}',
            "large_includes": r'{%\s*include.*%}'
        }

    def analyze_template(self, template_path: str) -> Dict[str, Any]:
        """Comprehensive analysis of a single template"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template_name = os.path.relpath(template_path, self.base_path)
            
            analysis = {
                "path": template_name,
                "size": len(content),
                "lines": len(content.splitlines()),
                "hash": hashlib.sha256(content.encode()).hexdigest()[:16],
                "syntax_valid": True,
                "variables": [],
                "blocks": [],
                "macros": [],
                "includes": [],
                "extends": None,
                "security_score": 100,
                "performance_score": 100,
                "complexity_score": 0,
                "issues": [],
                "recommendations": []
            }
            
            # Parse template for AST analysis
            try:
                ast = self.env.parse(content, name=template_name)
                analysis["variables"] = list(meta.find_undeclared_variables(ast))
                
                # Extract blocks, macros, includes
                for node in ast.find_all():
                    if hasattr(node, 'name'):
                        if node.__class__.__name__ == 'Block':
                            analysis["blocks"].append(node.name)
                        elif node.__class__.__name__ == 'Macro':
                            analysis["macros"].append(node.name)
                        elif node.__class__.__name__ == 'Include':
                            analysis["includes"].append(str(node.template))
                        elif node.__class__.__name__ == 'Extends':
                            analysis["extends"] = str(node.template)
                            
            except exceptions.TemplateSyntaxError as e:
                analysis["syntax_valid"] = False
                analysis["issues"].append(f"Syntax Error: {str(e)}")
                analysis["security_score"] -= 20
            
            # Security analysis
            self._analyze_security(content, analysis)
            
            # Performance analysis
            self._analyze_performance(content, analysis)
            
            # Complexity analysis
            self._analyze_complexity(content, analysis)
            
            # Best practices check
            self._check_best_practices(content, analysis)
            
            return analysis
            
        except Exception as e:
            return {
                "path": template_path,
                "error": str(e),
                "syntax_valid": False,
                "security_score": 0,
                "performance_score": 0
            }

    def _analyze_security(self, content: str, analysis: Dict[str, Any]):
        """Security vulnerability analysis"""
        security_issues = []
        
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    issue = {
                        "category": category,
                        "pattern": pattern,
                        "matches": len(matches),
                        "severity": "HIGH" if category == "hardcoded_secrets" else "MEDIUM"
                    }
                    security_issues.append(issue)
                    analysis["security_score"] -= 15 if issue["severity"] == "HIGH" else 10
        
        # Check for missing escaping
        if '{{' in content and '|e' not in content and '|escape' not in content:
            security_issues.append({
                "category": "missing_escaping",
                "description": "Template variables may not be properly escaped",
                "severity": "MEDIUM"
            })
            analysis["security_score"] -= 10
        
        analysis["security_issues"] = security_issues

    def _analyze_performance(self, content: str, analysis: Dict[str, Any]):
        """Performance optimization analysis"""
        perf_issues = []
        
        for issue_type, pattern in self.performance_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if matches:
                perf_issues.append({
                    "type": issue_type,
                    "count": len(matches),
                    "impact": "HIGH" if issue_type == "nested_loops" else "MEDIUM"
                })
                analysis["performance_score"] -= 20 if issue_type == "nested_loops" else 10
        
        # Check template size
        if analysis["lines"] > 200:
            perf_issues.append({
                "type": "large_template",
                "lines": analysis["lines"],
                "impact": "MEDIUM"
            })
            analysis["performance_score"] -= 15
        
        analysis["performance_issues"] = perf_issues

    def _analyze_complexity(self, content: str, analysis: Dict[str, Any]):
        """Template complexity analysis"""
        complexity = 0
        
        # Count control structures
        complexity += len(re.findall(r'{%\s*(if|for|while)', content))
        complexity += len(re.findall(r'{%\s*elif', content)) * 0.5
        complexity += len(re.findall(r'\|\s*\w+', content)) * 0.3  # Filters
        complexity += len(analysis["variables"]) * 0.1
        
        analysis["complexity_score"] = round(complexity, 2)
        
        if complexity > 20:
            analysis["recommendations"].append("Consider breaking down complex template into smaller components")

    def _check_best_practices(self, content: str, analysis: Dict[str, Any]):
        """Check Ansible/Jinja2 best practices"""
        recommendations = []
        
        # Check for documentation
        if not re.search(r'{#.*#}', content):
            recommendations.append("Add template documentation using {# comments #}")
        
        # Check for consistent indentation
        lines = content.splitlines()
        indent_pattern = None
        inconsistent_indent = False
        
        for line in lines:
            if line.strip() and line.startswith((' ', '\t')):
                current_indent = re.match(r'^(\s*)', line).group(1)
                if indent_pattern is None:
                    indent_pattern = 'spaces' if ' ' in current_indent else 'tabs'
                elif (indent_pattern == 'spaces' and '\t' in current_indent) or \
                     (indent_pattern == 'tabs' and ' ' in current_indent):
                    inconsistent_indent = True
                    break
        
        if inconsistent_indent:
            recommendations.append("Use consistent indentation (spaces or tabs, not mixed)")
        
        # Check for variable naming conventions
        for var in analysis["variables"]:
            if not re.match(r'^[a-z][a-z0-9_]*$', var):
                recommendations.append(f"Variable '{var}' doesn't follow snake_case convention")
        
        analysis["recommendations"].extend(recommendations)

    def analyze_inheritance_patterns(self, templates: List[str]) -> Dict[str, Any]:
        """Analyze template inheritance patterns"""
        inheritance_map = {}
        base_templates = set()
        child_templates = set()
        
        for template_path in templates:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                template_name = os.path.relpath(template_path, self.base_path)
                
                # Find extends
                extends_match = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']', content)
                if extends_match:
                    parent = extends_match.group(1)
                    inheritance_map[template_name] = {
                        "extends": parent,
                        "blocks": re.findall(r'{%\s*block\s+(\w+)', content),
                        "super_calls": len(re.findall(r'super\(\)', content))
                    }
                    child_templates.add(template_name)
                    base_templates.add(parent)
                
                # Find blocks in potential base templates
                blocks = re.findall(r'{%\s*block\s+(\w+)', content)
                if blocks and template_name not in child_templates:
                    inheritance_map[template_name] = {
                        "extends": None,
                        "blocks": blocks,
                        "super_calls": 0
                    }
            except Exception as e:
                # Skip templates that can't be read
                continue
        
        return {
            "inheritance_map": inheritance_map,
            "base_templates": list(base_templates),
            "child_templates": list(child_templates),
            "orphaned_templates": [t for t in templates if os.path.relpath(t, self.base_path) not in inheritance_map]
        }

    def validate_templates(self, template_list: List[str]) -> Dict[str, Any]:
        """Main validation function"""
        print(f"Analyzing {len(template_list)} templates...")
        
        total_issues = 0
        total_security_score = 0
        total_performance_score = 0
        
        for template_path in template_list:
            print(f"  Analyzing: {os.path.relpath(template_path, self.base_path)}")
            analysis = self.analyze_template(template_path)
            self.results["templates"][analysis["path"]] = analysis
            
            if "error" not in analysis:
                total_issues += len(analysis.get("issues", []))
                total_security_score += analysis.get("security_score", 0)
                total_performance_score += analysis.get("performance_score", 0)
        
        # Inheritance analysis
        self.results["inheritance_analysis"] = self.analyze_inheritance_patterns(template_list)
        
        # Summary
        valid_templates = len([t for t in self.results["templates"].values() if "error" not in t])
        self.results["summary"] = {
            "total_templates": len(template_list),
            "valid_templates": valid_templates,
            "invalid_templates": len(template_list) - valid_templates,
            "total_issues": total_issues,
            "average_security_score": round(total_security_score / max(valid_templates, 1), 2),
            "average_performance_score": round(total_performance_score / max(valid_templates, 1), 2),
            "inheritance_depth": len(self.results["inheritance_analysis"]["base_templates"])
        }
        
        return self.results

    def generate_report(self, output_file: str = None):
        """Generate comprehensive validation report"""
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"Report saved to: {output_file}")
        else:
            print(json.dumps(self.results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Ansible Template Quality Validator")
    parser.add_argument("--list", required=True, help="File containing list of templates to analyze")
    parser.add_argument("--out", default="template_analysis_report.json", help="Output report file")
    parser.add_argument("--base-path", default=".", help="Base path for template resolution")
    
    args = parser.parse_args()
    
    # Read template list
    with open(args.list, 'r') as f:
        templates = [line.strip() for line in f if line.strip()]
    
    # Validate templates
    validator = TemplateValidator(args.base_path)
    results = validator.validate_templates(templates)
    validator.generate_report(args.out)
    
    # Print summary
    summary = results["summary"]
    print(f"\n=== TEMPLATE VALIDATION SUMMARY ===")
    print(f"Total Templates: {summary['total_templates']}")
    print(f"Valid Templates: {summary['valid_templates']}")
    print(f"Invalid Templates: {summary['invalid_templates']}")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"Average Security Score: {summary['average_security_score']}/100")
    print(f"Average Performance Score: {summary['average_performance_score']}/100")
    print(f"Inheritance Depth: {summary['inheritance_depth']}")
    
    # Exit with error code if issues found
    if summary['total_issues'] > 0 or summary['invalid_templates'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
