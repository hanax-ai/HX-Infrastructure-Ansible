
#!/usr/bin/env python3
"""
Security Report Generation Script
Sprint 2 - Advanced Capabilities Implementation

This script aggregates security scan results from multiple tools and generates
comprehensive security reports in HTML and JSON formats.
"""

import json
import os
import sys
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from jinja2 import Template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityReportGenerator:
    """Generates comprehensive security reports from multiple scan tools."""
    
    def __init__(self):
        self.report_data = {
            'metadata': {
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'generator': 'HX-Infrastructure-Ansible Security Scanner',
                'version': '2.0.0'
            },
            'summary': {
                'total_vulnerabilities': 0,
                'critical_count': 0,
                'high_count': 0,
                'medium_count': 0,
                'low_count': 0,
                'tools_executed': [],
                'scan_coverage': {}
            },
            'vulnerabilities': [],
            'compliance': {
                'frameworks': [],
                'passed_checks': 0,
                'failed_checks': 0,
                'total_checks': 0
            },
            'recommendations': [],
            'tool_results': {}
        }
        
        # Tool configurations
        self.tool_configs = {
            'trivy': {
                'name': 'Trivy',
                'description': 'Container and filesystem vulnerability scanner',
                'file_patterns': ['trivy-*.sarif', 'trivy-*.json']
            },
            'kics': {
                'name': 'KICS',
                'description': 'Infrastructure as Code security scanner',
                'file_patterns': ['kics-results/*.sarif', 'kics-results/*.json']
            },
            'snyk': {
                'name': 'Snyk',
                'description': 'Software composition analysis and IaC scanner',
                'file_patterns': ['snyk*.sarif', 'snyk*.json']
            },
            'checkov': {
                'name': 'Checkov',
                'description': 'Static analysis for infrastructure as code',
                'file_patterns': ['checkov-*.sarif', 'checkov-*.json']
            },
            'bandit': {
                'name': 'Bandit',
                'description': 'Python security linter',
                'file_patterns': ['bandit-*.json', 'bandit-*.sarif']
            },
            'safety': {
                'name': 'Safety',
                'description': 'Python dependency vulnerability scanner',
                'file_patterns': ['safety-*.json']
            },
            'grype': {
                'name': 'Grype',
                'description': 'Container vulnerability scanner',
                'file_patterns': ['grype-*.sarif', 'grype-*.json']
            }
        }

    def collect_scan_results(self):
        """Collect and parse results from all security scanning tools."""
        logger.info("Collecting security scan results...")
        
        for tool_id, config in self.tool_configs.items():
            logger.info(f"Processing {config['name']} results...")
            
            tool_results = {
                'name': config['name'],
                'description': config['description'],
                'executed': False,
                'vulnerabilities': [],
                'file_processed': None,
                'errors': []
            }
            
            # Find result files for this tool
            result_files = []
            for pattern in config['file_patterns']:
                result_files.extend(glob.glob(pattern, recursive=True))
            
            if result_files:
                tool_results['executed'] = True
                self.report_data['summary']['tools_executed'].append(config['name'])
                
                for result_file in result_files:
                    try:
                        logger.info(f"Processing file: {result_file}")
                        tool_results['file_processed'] = result_file
                        
                        if result_file.endswith('.sarif'):
                            vulnerabilities = self._parse_sarif_file(result_file, tool_id)
                        elif result_file.endswith('.json'):
                            vulnerabilities = self._parse_json_file(result_file, tool_id)
                        else:
                            continue
                        
                        tool_results['vulnerabilities'].extend(vulnerabilities)
                        self.report_data['vulnerabilities'].extend(vulnerabilities)
                        
                    except Exception as e:
                        error_msg = f"Error processing {result_file}: {str(e)}"
                        logger.error(error_msg)
                        tool_results['errors'].append(error_msg)
            
            self.report_data['tool_results'][tool_id] = tool_results

    def _parse_sarif_file(self, file_path: str, tool_id: str) -> List[Dict[str, Any]]:
        """Parse SARIF format security scan results."""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r') as f:
                sarif_data = json.load(f)
            
            for run in sarif_data.get('runs', []):
                tool_name = run.get('tool', {}).get('driver', {}).get('name', tool_id)
                
                for result in run.get('results', []):
                    vulnerability = {
                        'id': result.get('ruleId', 'unknown'),
                        'title': result.get('message', {}).get('text', 'No title'),
                        'description': result.get('message', {}).get('text', 'No description'),
                        'severity': self._normalize_severity(result.get('level', 'info')),
                        'tool': tool_name,
                        'category': result.get('kind', 'vulnerability'),
                        'locations': [],
                        'cwe': [],
                        'cvss_score': None,
                        'remediation': None
                    }
                    
                    # Extract locations
                    for location in result.get('locations', []):
                        physical_location = location.get('physicalLocation', {})
                        artifact_location = physical_location.get('artifactLocation', {})
                        region = physical_location.get('region', {})
                        
                        vulnerability['locations'].append({
                            'file': artifact_location.get('uri', 'unknown'),
                            'line': region.get('startLine', 0),
                            'column': region.get('startColumn', 0)
                        })
                    
                    # Extract CWE information
                    for property_bag in result.get('properties', {}).values():
                        if isinstance(property_bag, dict) and 'cwe' in property_bag:
                            vulnerability['cwe'].append(property_bag['cwe'])
                    
                    vulnerabilities.append(vulnerability)
                    
        except Exception as e:
            logger.error(f"Error parsing SARIF file {file_path}: {e}")
            raise
        
        return vulnerabilities

    def _parse_json_file(self, file_path: str, tool_id: str) -> List[Dict[str, Any]]:
        """Parse JSON format security scan results."""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle different JSON structures based on tool
            if tool_id == 'safety':
                vulnerabilities = self._parse_safety_json(json_data)
            elif tool_id == 'bandit':
                vulnerabilities = self._parse_bandit_json(json_data)
            elif tool_id == 'trivy':
                vulnerabilities = self._parse_trivy_json(json_data)
            elif tool_id == 'snyk':
                vulnerabilities = self._parse_snyk_json(json_data)
            else:
                # Generic JSON parsing
                vulnerabilities = self._parse_generic_json(json_data, tool_id)
                
        except Exception as e:
            logger.error(f"Error parsing JSON file {file_path}: {e}")
            raise
        
        return vulnerabilities

    def _parse_safety_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Safety tool JSON results."""
        vulnerabilities = []
        
        for vuln in data.get('vulnerabilities', []):
            vulnerability = {
                'id': vuln.get('id', 'unknown'),
                'title': vuln.get('advisory', 'Unknown vulnerability'),
                'description': vuln.get('advisory', 'No description available'),
                'severity': self._normalize_severity(vuln.get('severity', 'medium')),
                'tool': 'Safety',
                'category': 'dependency',
                'locations': [{
                    'file': vuln.get('package_name', 'unknown'),
                    'line': 0,
                    'column': 0
                }],
                'cwe': [],
                'cvss_score': vuln.get('cvss_score'),
                'remediation': f"Update {vuln.get('package_name')} to version {vuln.get('safe_versions', 'latest')}"
            }
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    def _parse_bandit_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Bandit tool JSON results."""
        vulnerabilities = []
        
        for result in data.get('results', []):
            vulnerability = {
                'id': result.get('test_id', 'unknown'),
                'title': result.get('test_name', 'Unknown issue'),
                'description': result.get('issue_text', 'No description available'),
                'severity': self._normalize_severity(result.get('issue_severity', 'medium')),
                'tool': 'Bandit',
                'category': 'code_quality',
                'locations': [{
                    'file': result.get('filename', 'unknown'),
                    'line': result.get('line_number', 0),
                    'column': result.get('col_offset', 0)
                }],
                'cwe': [result.get('issue_cwe', {}).get('id')] if result.get('issue_cwe') else [],
                'cvss_score': None,
                'remediation': result.get('more_info', 'Review code for security issues')
            }
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    def _parse_trivy_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Trivy tool JSON results."""
        vulnerabilities = []
        
        for result in data.get('Results', []):
            target = result.get('Target', 'unknown')
            
            for vuln in result.get('Vulnerabilities', []):
                vulnerability = {
                    'id': vuln.get('VulnerabilityID', 'unknown'),
                    'title': vuln.get('Title', 'Unknown vulnerability'),
                    'description': vuln.get('Description', 'No description available'),
                    'severity': self._normalize_severity(vuln.get('Severity', 'medium')),
                    'tool': 'Trivy',
                    'category': 'vulnerability',
                    'locations': [{
                        'file': target,
                        'line': 0,
                        'column': 0
                    }],
                    'cwe': vuln.get('CweIDs', []),
                    'cvss_score': vuln.get('CVSS', {}).get('nvd', {}).get('V3Score'),
                    'remediation': vuln.get('FixedVersion', 'Update to latest version')
                }
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    def _parse_snyk_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Snyk tool JSON results."""
        vulnerabilities = []
        
        for vuln in data.get('vulnerabilities', []):
            vulnerability = {
                'id': vuln.get('id', 'unknown'),
                'title': vuln.get('title', 'Unknown vulnerability'),
                'description': vuln.get('description', 'No description available'),
                'severity': self._normalize_severity(vuln.get('severity', 'medium')),
                'tool': 'Snyk',
                'category': 'dependency',
                'locations': [{
                    'file': vuln.get('packageName', 'unknown'),
                    'line': 0,
                    'column': 0
                }],
                'cwe': vuln.get('identifiers', {}).get('CWE', []),
                'cvss_score': vuln.get('cvssScore'),
                'remediation': vuln.get('remediation', {}).get('advice', 'Update dependency')
            }
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    def _parse_generic_json(self, data: Dict[str, Any], tool_id: str) -> List[Dict[str, Any]]:
        """Parse generic JSON format results."""
        vulnerabilities = []
        
        # Try to find vulnerabilities in common JSON structures
        vuln_keys = ['vulnerabilities', 'issues', 'findings', 'results']
        
        for key in vuln_keys:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    vulnerability = {
                        'id': item.get('id', item.get('rule_id', 'unknown')),
                        'title': item.get('title', item.get('message', 'Unknown issue')),
                        'description': item.get('description', item.get('message', 'No description')),
                        'severity': self._normalize_severity(item.get('severity', 'medium')),
                        'tool': tool_id.title(),
                        'category': item.get('category', 'security'),
                        'locations': [{
                            'file': item.get('file', item.get('filename', 'unknown')),
                            'line': item.get('line', item.get('line_number', 0)),
                            'column': item.get('column', 0)
                        }],
                        'cwe': item.get('cwe', []),
                        'cvss_score': item.get('cvss_score'),
                        'remediation': item.get('remediation', 'Review and fix issue')
                    }
                    vulnerabilities.append(vulnerability)
                break
        
        return vulnerabilities

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels across different tools."""
        severity = severity.lower().strip()
        
        severity_mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'moderate': 'medium',
            'low': 'low',
            'info': 'low',
            'informational': 'low',
            'error': 'high',
            'warning': 'medium',
            'note': 'low'
        }
        
        return severity_mapping.get(severity, 'medium')

    def calculate_summary_statistics(self):
        """Calculate summary statistics from collected vulnerabilities."""
        logger.info("Calculating summary statistics...")
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for vuln in self.report_data['vulnerabilities']:
            severity = vuln.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        self.report_data['summary'].update({
            'total_vulnerabilities': len(self.report_data['vulnerabilities']),
            'critical_count': severity_counts['critical'],
            'high_count': severity_counts['high'],
            'medium_count': severity_counts['medium'],
            'low_count': severity_counts['low']
        })
        
        # Calculate scan coverage
        total_tools = len(self.tool_configs)
        executed_tools = len(self.report_data['summary']['tools_executed'])
        
        self.report_data['summary']['scan_coverage'] = {
            'total_tools': total_tools,
            'executed_tools': executed_tools,
            'coverage_percentage': (executed_tools / total_tools) * 100 if total_tools > 0 else 0
        }

    def generate_recommendations(self):
        """Generate security recommendations based on findings."""
        logger.info("Generating security recommendations...")
        
        recommendations = []
        summary = self.report_data['summary']
        
        # Critical vulnerabilities
        if summary['critical_count'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'vulnerability_management',
                'title': 'Address Critical Vulnerabilities Immediately',
                'description': f"Found {summary['critical_count']} critical vulnerabilities that require immediate attention.",
                'action': 'Review and patch all critical vulnerabilities before deployment.'
            })
        
        # High vulnerabilities
        if summary['high_count'] > 5:
            recommendations.append({
                'priority': 'high',
                'category': 'vulnerability_management',
                'title': 'High Vulnerability Count',
                'description': f"Found {summary['high_count']} high-severity vulnerabilities.",
                'action': 'Prioritize fixing high-severity vulnerabilities in the next sprint.'
            })
        
        # Scan coverage
        if summary['scan_coverage']['coverage_percentage'] < 80:
            recommendations.append({
                'priority': 'medium',
                'category': 'tooling',
                'title': 'Improve Security Scan Coverage',
                'description': f"Only {summary['scan_coverage']['coverage_percentage']:.1f}% of security tools executed successfully.",
                'action': 'Investigate and fix security tool configuration issues.'
            })
        
        # Tool-specific recommendations
        for tool_id, tool_result in self.report_data['tool_results'].items():
            if tool_result['errors']:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'tooling',
                    'title': f'Fix {tool_result["name"]} Execution Issues',
                    'description': f"Errors occurred while running {tool_result['name']}.",
                    'action': f'Review and fix {tool_result["name"]} configuration and dependencies.'
                })
        
        # General recommendations
        if summary['total_vulnerabilities'] == 0:
            recommendations.append({
                'priority': 'info',
                'category': 'security_posture',
                'title': 'Excellent Security Posture',
                'description': 'No vulnerabilities detected in current scan.',
                'action': 'Continue following security best practices and regular scanning.'
            })
        
        self.report_data['recommendations'] = recommendations

    def generate_html_report(self, output_file: str = 'security-report.html'):
        """Generate HTML security report."""
        logger.info(f"Generating HTML report: {output_file}")
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Scan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #eee; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; border-left: 4px solid #007bff; }
        .summary-card.critical { border-left-color: #dc3545; }
        .summary-card.high { border-left-color: #fd7e14; }
        .summary-card.medium { border-left-color: #ffc107; }
        .summary-card.low { border-left-color: #28a745; }
        .summary-card h3 { margin: 0 0 10px 0; color: #333; }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #007bff; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .vulnerability { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 15px; margin-bottom: 15px; }
        .vulnerability.critical { border-left: 4px solid #dc3545; }
        .vulnerability.high { border-left: 4px solid #fd7e14; }
        .vulnerability.medium { border-left: 4px solid #ffc107; }
        .vulnerability.low { border-left: 4px solid #28a745; }
        .vulnerability h4 { margin: 0 0 10px 0; color: #333; }
        .vulnerability .meta { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        .vulnerability .description { margin-bottom: 10px; }
        .vulnerability .location { background: #f8f9fa; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }
        .recommendations { background: #e7f3ff; padding: 20px; border-radius: 6px; border-left: 4px solid #007bff; }
        .recommendation { margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; }
        .recommendation.critical { border-left: 3px solid #dc3545; }
        .recommendation.high { border-left: 3px solid #fd7e14; }
        .recommendation.medium { border-left: 3px solid #ffc107; }
        .recommendation.info { border-left: 3px solid #17a2b8; }
        .tools-executed { background: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .tools-executed ul { margin: 0; padding-left: 20px; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Scan Report</h1>
            <p>Generated on {{ report_data.metadata.generated_at }}</p>
            <p>{{ report_data.metadata.generator }} v{{ report_data.metadata.version }}</p>
        </div>

        <div class="summary">
            <div class="summary-card critical">
                <h3>Critical</h3>
                <div class="number">{{ report_data.summary.critical_count }}</div>
            </div>
            <div class="summary-card high">
                <h3>High</h3>
                <div class="number">{{ report_data.summary.high_count }}</div>
            </div>
            <div class="summary-card medium">
                <h3>Medium</h3>
                <div class="number">{{ report_data.summary.medium_count }}</div>
            </div>
            <div class="summary-card low">
                <h3>Low</h3>
                <div class="number">{{ report_data.summary.low_count }}</div>
            </div>
            <div class="summary-card">
                <h3>Total</h3>
                <div class="number">{{ report_data.summary.total_vulnerabilities }}</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Scan Coverage</h2>
            <div class="tools-executed">
                <p><strong>Tools Executed:</strong> {{ report_data.summary.scan_coverage.executed_tools }}/{{ report_data.summary.scan_coverage.total_tools }} ({{ "%.1f"|format(report_data.summary.scan_coverage.coverage_percentage) }}%)</p>
                <ul>
                    {% for tool in report_data.summary.tools_executed %}
                    <li>{{ tool }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        {% if report_data.vulnerabilities %}
        <div class="section">
            <h2>🚨 Vulnerabilities</h2>
            {% for vuln in report_data.vulnerabilities %}
            <div class="vulnerability {{ vuln.severity }}">
                <h4>{{ vuln.title }}</h4>
                <div class="meta">
                    <strong>ID:</strong> {{ vuln.id }} | 
                    <strong>Severity:</strong> {{ vuln.severity.title() }} | 
                    <strong>Tool:</strong> {{ vuln.tool }} | 
                    <strong>Category:</strong> {{ vuln.category }}
                    {% if vuln.cvss_score %}
                    | <strong>CVSS:</strong> {{ vuln.cvss_score }}
                    {% endif %}
                </div>
                <div class="description">{{ vuln.description }}</div>
                {% if vuln.locations %}
                <div class="location">
                    <strong>Location:</strong> {{ vuln.locations[0].file }}
                    {% if vuln.locations[0].line > 0 %}:{{ vuln.locations[0].line }}{% endif %}
                </div>
                {% endif %}
                {% if vuln.remediation %}
                <div class="remediation">
                    <strong>Remediation:</strong> {{ vuln.remediation }}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if report_data.recommendations %}
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div class="recommendations">
                {% for rec in report_data.recommendations %}
                <div class="recommendation {{ rec.priority }}">
                    <h4>{{ rec.title }}</h4>
                    <p><strong>Priority:</strong> {{ rec.priority.title() }} | <strong>Category:</strong> {{ rec.category.replace('_', ' ').title() }}</p>
                    <p>{{ rec.description }}</p>
                    <p><strong>Action:</strong> {{ rec.action }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div class="footer">
            <p>This report was automatically generated by the HX-Infrastructure-Ansible security scanning pipeline.</p>
            <p>For questions or issues, please contact the DevSecOps team.</p>
        </div>
    </div>
</body>
</html>
        """
        
        try:
            template = Template(html_template)
            html_content = template.render(report_data=self.report_data)
            
            with open(output_file, 'w') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated successfully: {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise

    def generate_json_report(self, output_file: str = 'security-report.json'):
        """Generate JSON security report."""
        logger.info(f"Generating JSON report: {output_file}")
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.report_data, f, indent=2, default=str)
            
            logger.info(f"JSON report generated successfully: {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            raise

    def generate_summary_markdown(self, output_file: str = 'security-summary.md'):
        """Generate markdown summary for PR comments."""
        logger.info(f"Generating markdown summary: {output_file}")
        
        summary = self.report_data['summary']
        
        markdown_content = f"""## 🔒 Security Scan Summary

**Scan completed:** {self.report_data['metadata']['generated_at']}

### 📊 Vulnerability Overview
| Severity | Count |
|----------|-------|
| 🔴 Critical | {summary['critical_count']} |
| 🟠 High | {summary['high_count']} |
| 🟡 Medium | {summary['medium_count']} |
| 🟢 Low | {summary['low_count']} |
| **Total** | **{summary['total_vulnerabilities']}** |

### 🛠️ Tools Executed
**Coverage:** {summary['scan_coverage']['executed_tools']}/{summary['scan_coverage']['total_tools']} tools ({summary['scan_coverage']['coverage_percentage']:.1f}%)

{chr(10).join([f"- ✅ {tool}" for tool in summary['tools_executed']])}

### 🚨 Action Required
"""
        
        if summary['critical_count'] > 0:
            markdown_content += f"- ❌ **CRITICAL:** {summary['critical_count']} critical vulnerabilities must be fixed before deployment\n"
        
        if summary['high_count'] > 5:
            markdown_content += f"- ⚠️ **HIGH:** {summary['high_count']} high-severity vulnerabilities should be addressed\n"
        
        if summary['total_vulnerabilities'] == 0:
            markdown_content += "- ✅ **EXCELLENT:** No vulnerabilities detected!\n"
        
        markdown_content += f"""
### 📋 Top Recommendations
"""
        
        for rec in self.report_data['recommendations'][:3]:  # Top 3 recommendations
            priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'info': '🔵'}.get(rec['priority'], '⚪')
            markdown_content += f"- {priority_emoji} **{rec['title']}:** {rec['description']}\n"
        
        markdown_content += f"""
---
📄 **Full Report:** [security-report.html](security-report.html) | [security-report.json](security-report.json)
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown summary generated successfully: {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating markdown summary: {e}")
            raise

    def generate_all_reports(self):
        """Generate all report formats."""
        logger.info("Generating comprehensive security reports...")
        
        # Collect scan results
        self.collect_scan_results()
        
        # Calculate statistics
        self.calculate_summary_statistics()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Generate all report formats
        self.generate_json_report()
        self.generate_html_report()
        self.generate_summary_markdown()
        
        logger.info("All security reports generated successfully!")
        
        # Print summary to console
        self._print_console_summary()

    def _print_console_summary(self):
        """Print security summary to console."""
        summary = self.report_data['summary']
        
        print("\n" + "="*60)
        print("SECURITY SCAN SUMMARY")
        print("="*60)
        print(f"Total Vulnerabilities: {summary['total_vulnerabilities']}")
        print(f"  Critical: {summary['critical_count']}")
        print(f"  High: {summary['high_count']}")
        print(f"  Medium: {summary['medium_count']}")
        print(f"  Low: {summary['low_count']}")
        print(f"\nScan Coverage: {summary['scan_coverage']['coverage_percentage']:.1f}%")
        print(f"Tools Executed: {', '.join(summary['tools_executed'])}")
        
        if summary['critical_count'] > 0:
            print(f"\n❌ CRITICAL: {summary['critical_count']} critical vulnerabilities require immediate attention!")
        elif summary['high_count'] > 5:
            print(f"\n⚠️  WARNING: {summary['high_count']} high-severity vulnerabilities detected")
        elif summary['total_vulnerabilities'] == 0:
            print("\n✅ EXCELLENT: No vulnerabilities detected!")
        else:
            print(f"\n✅ GOOD: {summary['total_vulnerabilities']} vulnerabilities detected (no critical/high)")
        
        print("="*60)

def main():
    """Main execution function."""
    logger.info("Starting Security Report Generation")
    
    try:
        generator = SecurityReportGenerator()
        generator.generate_all_reports()
        
        # Exit with appropriate code based on critical vulnerabilities
        critical_count = generator.report_data['summary']['critical_count']
        sys.exit(1 if critical_count > 0 else 0)
        
    except Exception as e:
        logger.error(f"Security report generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

