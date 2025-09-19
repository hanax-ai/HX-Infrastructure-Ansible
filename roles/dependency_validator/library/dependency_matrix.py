
#!/usr/bin/env python3
"""
Dependency Matrix Generator - Phase 3 Day 1
Advanced dependency validation and compatibility checking
"""

import json
import sys
import subprocess
import platform
import socket
import ssl
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: dependency_matrix
short_description: Generate comprehensive dependency matrix and compatibility report
description:
    - Validates system dependencies and generates compatibility matrix
    - Checks version compatibility across components
    - Provides detailed dependency resolution information
options:
    dependencies:
        description: List of dependencies to validate
        required: true
        type: list
    output_path:
        description: Path to save the dependency matrix report
        required: false
        type: str
        default: /tmp/dependency_matrix.json
    check_versions:
        description: Whether to perform version compatibility checking
        required: false
        type: bool
        default: true
'''

EXAMPLES = '''
- name: Generate dependency matrix
  dependency_matrix:
    dependencies:
      - name: python3
        type: package
        min_version: "3.6"
      - name: openssl
        type: package
        min_version: "1.1.1"
    output_path: /tmp/deps.json
'''

def check_package_version(package_name):
    """Check installed package version"""
    try:
        if package_name == 'python3':
            result = subprocess.run(['python3', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return {'installed': True, 'version': version}
        
        elif package_name == 'openssl':
            result = subprocess.run(['openssl', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[1]
                return {'installed': True, 'version': version}
        
        elif package_name == 'curl':
            result = subprocess.run(['curl', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0].split()[1]
                return {'installed': True, 'version': version}
        
        # Generic package check
        result = subprocess.run(['which', package_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return {'installed': True, 'version': 'unknown'}
        
        return {'installed': False, 'version': None}
    
    except Exception as e:
        return {'installed': False, 'version': None, 'error': str(e)}

def check_network_connectivity(host, port, timeout=5):
    """Check network connectivity to host:port"""
    try:
        sock = socket.create_connection((host, port), timeout)
        sock.close()
        return {'reachable': True, 'latency': 'low'}
    except Exception as e:
        return {'reachable': False, 'error': str(e)}

def check_ssl_certificate(hostname, port=443):
    """Check SSL certificate validity"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return {
                    'valid': True,
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'expires': cert['notAfter']
                }
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def generate_system_info():
    """Generate comprehensive system information"""
    return {
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'hostname': socket.gethostname(),
        'timestamp': datetime.now().isoformat()
    }

def compare_versions(version1, version2):
    """Compare two version strings"""
    try:
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        return 0
    except:
        return 0  # Unable to compare

def main():
    module_args = dict(
        dependencies=dict(type='list', required=True),
        output_path=dict(type='str', required=False, default='/tmp/dependency_matrix.json'),
        check_versions=dict(type='bool', required=False, default=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    dependencies = module.params['dependencies']
    output_path = module.params['output_path']
    check_versions = module.params['check_versions']

    # Generate dependency matrix
    matrix = {
        'system_info': generate_system_info(),
        'dependencies': {},
        'compatibility_matrix': {},
        'validation_summary': {
            'total_dependencies': len(dependencies),
            'satisfied_dependencies': 0,
            'failed_dependencies': 0,
            'warnings': []
        }
    }

    # Check each dependency
    for dep in dependencies:
        dep_name = dep.get('name', '')
        dep_type = dep.get('type', 'package')
        min_version = dep.get('min_version', None)
        
        if dep_type == 'package':
            result = check_package_version(dep_name)
            matrix['dependencies'][dep_name] = result
            
            if result['installed']:
                matrix['validation_summary']['satisfied_dependencies'] += 1
                
                # Version compatibility check
                if check_versions and min_version and result['version'] != 'unknown':
                    comparison = compare_versions(result['version'], min_version)
                    if comparison < 0:
                        matrix['validation_summary']['warnings'].append(
                            f"{dep_name} version {result['version']} is below minimum {min_version}"
                        )
            else:
                matrix['validation_summary']['failed_dependencies'] += 1
        
        elif dep_type == 'network':
            host = dep.get('host', '')
            port = dep.get('port', 80)
            result = check_network_connectivity(host, port)
            matrix['dependencies'][f"{host}:{port}"] = result
            
            if result['reachable']:
                matrix['validation_summary']['satisfied_dependencies'] += 1
            else:
                matrix['validation_summary']['failed_dependencies'] += 1
        
        elif dep_type == 'ssl':
            hostname = dep.get('hostname', '')
            port = dep.get('port', 443)
            result = check_ssl_certificate(hostname, port)
            matrix['dependencies'][f"ssl:{hostname}:{port}"] = result
            
            if result['valid']:
                matrix['validation_summary']['satisfied_dependencies'] += 1
            else:
                matrix['validation_summary']['failed_dependencies'] += 1

    # Generate compatibility matrix
    matrix['compatibility_matrix'] = {
        'os_compatibility': {
            'supported': True,
            'platform': platform.platform(),
            'recommendations': []
        },
        'version_compatibility': {
            'python_compatible': platform.python_version() >= '3.6',
            'recommendations': []
        }
    }

    # Save matrix to file
    try:
        with open(output_path, 'w') as f:
            json.dump(matrix, f, indent=2)
        
        module.exit_json(
            changed=True,
            dependency_matrix=matrix,
            output_path=output_path,
            msg=f"Dependency matrix generated successfully with {matrix['validation_summary']['satisfied_dependencies']}/{matrix['validation_summary']['total_dependencies']} dependencies satisfied"
        )
    
    except Exception as e:
        module.fail_json(msg=f"Failed to generate dependency matrix: {str(e)}")

if __name__ == '__main__':
    main()

