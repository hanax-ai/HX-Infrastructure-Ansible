
#!/usr/bin/env python3
"""
Performance Report Generator for HX Infrastructure Ansible
Generates comprehensive performance metrics and benchmarks
"""

import json
import time
import subprocess
import psutil
import os
from pathlib import Path
from typing import Dict, List, Any
import statistics


class PerformanceReporter:
    """Generate comprehensive performance reports"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.metrics = {
            'linting_performance': {},
            'syntax_check_performance': {},
            'role_loading_performance': {},
            'system_metrics': {},
            'scalability_metrics': {}
        }
    
    def measure_linting_performance(self) -> Dict[str, Any]:
        """Measure ansible-lint and yamllint performance"""
        print("⚡ Measuring linting performance...")
        
        results = {}
        
        # Measure ansible-lint performance
        try:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = subprocess.run(
                ['ansible-lint', '--format', 'json', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            results['ansible_lint'] = {
                'duration': round(end_time - start_time, 2),
                'memory_usage': round(end_memory - start_memory, 2),
                'exit_code': result.returncode,
                'issues_found': 0
            }
            
            # Count issues if JSON output is valid
            try:
                lint_data = json.loads(result.stdout)
                results['ansible_lint']['issues_found'] = len(lint_data)
            except json.JSONDecodeError:
                pass
                
        except Exception as e:
            results['ansible_lint'] = {'error': str(e)}
        
        # Measure yamllint performance
        try:
            start_time = time.time()
            
            result = subprocess.run(
                ['yamllint', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            end_time = time.time()
            
            results['yamllint'] = {
                'duration': round(end_time - start_time, 2),
                'exit_code': result.returncode,
                'lines_checked': len(result.stdout.splitlines())
            }
            
        except Exception as e:
            results['yamllint'] = {'error': str(e)}
        
        self.metrics['linting_performance'] = results
        return results
    
    def measure_syntax_check_performance(self) -> Dict[str, Any]:
        """Measure playbook syntax checking performance"""
        print("📝 Measuring syntax check performance...")
        
        results = {}
        
        # Find all playbooks
        playbooks = []
        for pattern in ['*.yml', 'playbooks/*.yml']:
            playbooks.extend(self.project_root.glob(pattern))
        
        playbook_results = []
        
        for playbook in playbooks:
            if playbook.name in ['site.yml'] or 'playbook' in playbook.name.lower():
                try:
                    start_time = time.time()
                    
                    result = subprocess.run([
                        'ansible-playbook',
                        '--syntax-check',
                        '--inventory', 'inventories/dev/hosts.yml',
                        str(playbook)
                    ], cwd=self.project_root, capture_output=True, text=True)
                    
                    end_time = time.time()
                    
                    playbook_results.append({
                        'playbook': playbook.name,
                        'duration': round(end_time - start_time, 2),
                        'exit_code': result.returncode
                    })
                    
                except Exception as e:
                    playbook_results.append({
                        'playbook': playbook.name,
                        'error': str(e)
                    })
        
        if playbook_results:
            durations = [r['duration'] for r in playbook_results if 'duration' in r]
            results = {
                'playbooks_tested': len(playbook_results),
                'total_duration': round(sum(durations), 2),
                'average_duration': round(statistics.mean(durations), 2) if durations else 0,
                'max_duration': round(max(durations), 2) if durations else 0,
                'min_duration': round(min(durations), 2) if durations else 0,
                'details': playbook_results
            }
        
        self.metrics['syntax_check_performance'] = results
        return results
    
    def measure_role_loading_performance(self) -> Dict[str, Any]:
        """Measure role loading and parsing performance"""
        print("🎭 Measuring role loading performance...")
        
        results = {}
        roles_dir = self.project_root / 'roles'
        
        if not roles_dir.exists():
            results['error'] = 'Roles directory not found'
            return results
        
        role_results = []
        total_start_time = time.time()
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                start_time = time.time()
                
                role_info = {
                    'role_name': role_dir.name,
                    'files_loaded': 0,
                    'errors': []
                }
                
                # Load role files
                role_files = [
                    'meta/main.yml',
                    'defaults/main.yml',
                    'vars/main.yml',
                    'tasks/main.yml',
                    'handlers/main.yml'
                ]
                
                for role_file in role_files:
                    file_path = role_dir / role_file
                    if file_path.exists():
                        try:
                            import yaml
                            with open(file_path, 'r') as f:
                                yaml.safe_load(f)
                            role_info['files_loaded'] += 1
                        except Exception as e:
                            role_info['errors'].append(f"{role_file}: {str(e)}")
                
                end_time = time.time()
                role_info['duration'] = round(end_time - start_time, 3)
                role_results.append(role_info)
        
        total_end_time = time.time()
        
        durations = [r['duration'] for r in role_results]
        results = {
            'total_roles': len(role_results),
            'total_duration': round(total_end_time - total_start_time, 2),
            'average_role_duration': round(statistics.mean(durations), 3) if durations else 0,
            'max_role_duration': round(max(durations), 3) if durations else 0,
            'roles_with_errors': len([r for r in role_results if r['errors']]),
            'details': role_results
        }
        
        self.metrics['role_loading_performance'] = results
        return results
    
    def measure_system_metrics(self) -> Dict[str, Any]:
        """Measure current system performance metrics"""
        print("💻 Measuring system metrics...")
        
        results = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('.').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            'process_count': len(psutil.pids())
        }
        
        # Add disk I/O if available
        try:
            disk_io = psutil.disk_io_counters()
            results['disk_io'] = {
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes
            }
        except Exception:
            pass
        
        # Add network I/O if available
        try:
            net_io = psutil.net_io_counters()
            results['network_io'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
        except Exception:
            pass
        
        self.metrics['system_metrics'] = results
        return results
    
    def measure_scalability_metrics(self) -> Dict[str, Any]:
        """Measure scalability-related metrics"""
        print("📈 Measuring scalability metrics...")
        
        results = {}
        
        # Count project artifacts
        results['project_size'] = {
            'total_files': len(list(self.project_root.rglob('*'))),
            'yaml_files': len(list(self.project_root.rglob('*.yml'))),
            'python_files': len(list(self.project_root.rglob('*.py'))),
            'roles_count': len([
                d for d in (self.project_root / 'roles').iterdir()
                if d.is_dir() and not d.name.startswith('.')
            ]) if (self.project_root / 'roles').exists() else 0,
            'playbooks_count': len(list(self.project_root.glob('*.yml'))) + 
                             len(list((self.project_root / 'playbooks').glob('*.yml')))
                             if (self.project_root / 'playbooks').exists() else 0
        }
        
        # Estimate complexity
        total_lines = 0
        yaml_files = list(self.project_root.rglob('*.yml'))
        
        for yaml_file in yaml_files[:50]:  # Sample first 50 files
            try:
                with open(yaml_file, 'r') as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass
        
        results['complexity_metrics'] = {
            'estimated_total_lines': total_lines * (len(yaml_files) / min(50, len(yaml_files))),
            'average_lines_per_file': total_lines / min(50, len(yaml_files)) if yaml_files else 0
        }
        
        self.metrics['scalability_metrics'] = results
        return results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("\n🚀 Generating performance report...")
        
        # Run all measurements
        self.measure_linting_performance()
        self.measure_syntax_check_performance()
        self.measure_role_loading_performance()
        self.measure_system_metrics()
        self.measure_scalability_metrics()
        
        # Generate summary
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'performance_metrics': self.metrics,
            'summary': self.generate_summary(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        summary = {}
        
        # Linting performance summary
        if 'ansible_lint' in self.metrics['linting_performance']:
            lint_duration = self.metrics['linting_performance']['ansible_lint'].get('duration', 0)
            summary['linting_speed'] = 'Fast' if lint_duration < 30 else 'Moderate' if lint_duration < 60 else 'Slow'
        
        # Syntax check summary
        if 'average_duration' in self.metrics['syntax_check_performance']:
            avg_syntax = self.metrics['syntax_check_performance']['average_duration']
            summary['syntax_check_speed'] = 'Fast' if avg_syntax < 5 else 'Moderate' if avg_syntax < 15 else 'Slow'
        
        # Role loading summary
        if 'average_role_duration' in self.metrics['role_loading_performance']:
            avg_role = self.metrics['role_loading_performance']['average_role_duration']
            summary['role_loading_speed'] = 'Fast' if avg_role < 0.1 else 'Moderate' if avg_role < 0.5 else 'Slow'
        
        # System health
        if 'cpu_percent' in self.metrics['system_metrics']:
            cpu = self.metrics['system_metrics']['cpu_percent']
            memory = self.metrics['system_metrics']['memory_percent']
            summary['system_health'] = 'Good' if cpu < 50 and memory < 80 else 'Moderate' if cpu < 80 and memory < 90 else 'High Load'
        
        return summary
    
    def generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check linting performance
        if 'ansible_lint' in self.metrics['linting_performance']:
            duration = self.metrics['linting_performance']['ansible_lint'].get('duration', 0)
            if duration > 60:
                recommendations.append("Consider optimizing ansible-lint configuration to improve performance")
        
        # Check syntax performance
        if 'average_duration' in self.metrics['syntax_check_performance']:
            avg_duration = self.metrics['syntax_check_performance']['average_duration']
            if avg_duration > 10:
                recommendations.append("Optimize playbook structure to improve syntax check speed")
        
        # Check role loading
        if 'roles_with_errors' in self.metrics['role_loading_performance']:
            errors = self.metrics['role_loading_performance']['roles_with_errors']
            if errors > 0:
                recommendations.append(f"Fix {errors} roles with loading errors to improve performance")
        
        # Check system resources
        if 'memory_percent' in self.metrics['system_metrics']:
            memory = self.metrics['system_metrics']['memory_percent']
            if memory > 80:
                recommendations.append("Consider increasing system memory for better performance")
        
        # Check project size
        if 'total_files' in self.metrics['scalability_metrics']['project_size']:
            total_files = self.metrics['scalability_metrics']['project_size']['total_files']
            if total_files > 1000:
                recommendations.append("Consider organizing large project into smaller modules")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any]) -> None:
        """Save performance report to file"""
        report_file = self.reports_dir / 'performance_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Performance report saved to: {report_file}")
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print performance summary"""
        print("\n" + "="*60)
        print("🚀 HX INFRASTRUCTURE ANSIBLE - PERFORMANCE REPORT")
        print("="*60)
        
        summary = report['summary']
        
        print("📊 Performance Summary:")
        for metric, value in summary.items():
            status = "✅" if value == 'Fast' or value == 'Good' else "⚠️" if 'Moderate' in value else "❌"
            print(f"  {status} {metric.replace('_', ' ').title()}: {value}")
        
        # Show key metrics
        metrics = report['performance_metrics']
        
        if 'ansible_lint' in metrics['linting_performance']:
            lint_data = metrics['linting_performance']['ansible_lint']
            print(f"\n⚡ Ansible Lint: {lint_data.get('duration', 0)}s, {lint_data.get('issues_found', 0)} issues")
        
        if 'average_duration' in metrics['syntax_check_performance']:
            syntax_data = metrics['syntax_check_performance']
            print(f"📝 Syntax Check: {syntax_data['average_duration']}s average, {syntax_data['playbooks_tested']} playbooks")
        
        if 'total_roles' in metrics['role_loading_performance']:
            role_data = metrics['role_loading_performance']
            print(f"🎭 Role Loading: {role_data['total_duration']}s total, {role_data['total_roles']} roles")
        
        # Show recommendations
        if report['recommendations']:
            print("\n💡 Performance Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Main execution function"""
    reporter = PerformanceReporter()
    report = reporter.generate_performance_report()
    
    reporter.save_report(report)
    reporter.print_summary(report)
    
    return report


if __name__ == '__main__':
    main()
