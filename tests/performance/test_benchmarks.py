
"""
Performance benchmarks for Ansible playbooks and roles
Measures execution time, resource usage, and scalability
"""

import pytest
import subprocess
import time
import psutil
import json
import tempfile
from pathlib import Path
import yaml
import statistics
from contextlib import contextmanager


class PerformanceMetrics:
    """Helper class to collect and analyze performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'execution_time': [],
            'memory_usage': [],
            'cpu_usage': [],
            'disk_io': [],
            'network_io': []
        }
    
    def add_execution_time(self, duration):
        self.metrics['execution_time'].append(duration)
    
    def add_resource_usage(self, memory, cpu, disk_io=0, network_io=0):
        self.metrics['memory_usage'].append(memory)
        self.metrics['cpu_usage'].append(cpu)
        self.metrics['disk_io'].append(disk_io)
        self.metrics['network_io'].append(network_io)
    
    def get_summary(self):
        summary = {}
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'count': len(values)
                }
        return summary


@contextmanager
def performance_monitor():
    """Context manager to monitor system performance during execution"""
    process = psutil.Process()
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_cpu = process.cpu_percent()
    
    yield
    
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    end_cpu = process.cpu_percent()
    
    return {
        'duration': end_time - start_time,
        'memory_delta': end_memory - start_memory,
        'cpu_usage': (start_cpu + end_cpu) / 2
    }


class TestPlaybookPerformance:
    """Test performance of Ansible playbooks"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def performance_metrics(self):
        return PerformanceMetrics()
    
    def test_syntax_check_performance(self, project_root, performance_metrics):
        """Benchmark syntax checking performance"""
        playbooks = [
            'site.yml',
            'playbooks/safety_test.yml',
            'playbooks/phase3_integration_test.yml'
        ]
        
        for playbook in playbooks:
            playbook_path = project_root / playbook
            if playbook_path.exists():
                start_time = time.time()
                
                cmd = [
                    'ansible-playbook',
                    '--syntax-check',
                    '--inventory', str(project_root / 'inventories' / 'dev' / 'hosts.yml'),
                    str(playbook_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
                
                end_time = time.time()
                duration = end_time - start_time
                
                performance_metrics.add_execution_time(duration)
                
                # Syntax check should complete quickly
                assert duration < 30, f"Syntax check for {playbook} took too long: {duration:.2f}s"
                assert result.returncode == 0, f"Syntax check failed for {playbook}"
    
    def test_dry_run_performance(self, project_root, performance_metrics):
        """Benchmark dry run performance"""
        # Test with a simple playbook
        test_playbook = project_root / 'playbooks' / 'safety_test.yml'
        
        if test_playbook.exists():
            start_time = time.time()
            
            cmd = [
                'ansible-playbook',
                '--check',
                '--diff',
                '--inventory', str(project_root / 'inventories' / 'dev' / 'hosts.yml'),
                str(test_playbook)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            
            end_time = time.time()
            duration = end_time - start_time
            
            performance_metrics.add_execution_time(duration)
            
            # Dry run should complete within reasonable time
            assert duration < 60, f"Dry run took too long: {duration:.2f}s"
    
    def test_ansible_lint_performance(self, project_root, performance_metrics):
        """Benchmark ansible-lint performance"""
        start_time = time.time()
        
        cmd = ['ansible-lint', '--format', 'json', '.']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        end_time = time.time()
        duration = end_time - start_time
        
        performance_metrics.add_execution_time(duration)
        
        # Linting should complete within reasonable time
        assert duration < 120, f"Ansible-lint took too long: {duration:.2f}s"


class TestRolePerformance:
    """Test performance of individual roles"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_role_loading_performance(self, project_root):
        """Test how quickly roles can be loaded and parsed"""
        roles_dir = project_root / 'roles'
        
        start_time = time.time()
        role_count = 0
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                role_count += 1
                
                # Load role metadata
                meta_file = role_dir / 'meta' / 'main.yml'
                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        yaml.safe_load(f)
                
                # Load role defaults
                defaults_file = role_dir / 'defaults' / 'main.yml'
                if defaults_file.exists():
                    with open(defaults_file, 'r') as f:
                        yaml.safe_load(f)
                
                # Load role tasks
                tasks_file = role_dir / 'tasks' / 'main.yml'
                if tasks_file.exists():
                    with open(tasks_file, 'r') as f:
                        yaml.safe_load(f)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be able to load all roles quickly
        avg_time_per_role = duration / max(role_count, 1)
        assert avg_time_per_role < 1.0, f"Role loading too slow: {avg_time_per_role:.2f}s per role"
    
    def test_template_rendering_performance(self, project_root):
        """Test template rendering performance"""
        from jinja2 import Environment, FileSystemLoader
        
        roles_dir = project_root / 'roles'
        template_count = 0
        start_time = time.time()
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                templates_dir = role_dir / 'templates'
                if templates_dir.exists():
                    env = Environment(loader=FileSystemLoader(str(templates_dir)))
                    
                    for template_file in templates_dir.glob('*'):
                        if template_file.is_file() and not template_file.name.startswith('.'):
                            try:
                                template = env.get_template(template_file.name)
                                # Render with minimal context
                                template.render({})
                                template_count += 1
                            except Exception:
                                # Skip templates that require specific context
                                pass
        
        end_time = time.time()
        duration = end_time - start_time
        
        if template_count > 0:
            avg_time_per_template = duration / template_count
            assert avg_time_per_template < 0.5, f"Template rendering too slow: {avg_time_per_template:.2f}s per template"


class TestScalabilityBenchmarks:
    """Test scalability with different inventory sizes"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def create_test_inventory(self, host_count):
        """Create a test inventory with specified number of hosts"""
        inventory_data = {
            'all': {
                'children': {
                    'test_group': {
                        'hosts': {}
                    }
                }
            }
        }
        
        for i in range(host_count):
            inventory_data['all']['children']['test_group']['hosts'][f'test-host-{i:03d}'] = {
                'ansible_host': f'192.168.1.{i + 10}',
                'ansible_user': 'test'
            }
        
        return inventory_data
    
    def test_inventory_parsing_scalability(self, project_root):
        """Test inventory parsing with different sizes"""
        host_counts = [10, 50, 100]
        
        for host_count in host_counts:
            inventory_data = self.create_test_inventory(host_count)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                yaml.dump(inventory_data, f)
                temp_inventory = f.name
            
            try:
                start_time = time.time()
                
                cmd = [
                    'ansible-inventory',
                    '--inventory', temp_inventory,
                    '--list'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Parsing should scale reasonably
                assert duration < host_count * 0.01 + 5, \
                    f"Inventory parsing too slow for {host_count} hosts: {duration:.2f}s"
                assert result.returncode == 0, f"Inventory parsing failed for {host_count} hosts"
                
            finally:
                Path(temp_inventory).unlink()


class TestMemoryUsage:
    """Test memory usage patterns"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_memory_usage_during_linting(self, project_root):
        """Monitor memory usage during ansible-lint execution"""
        import psutil
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        cmd = ['ansible-lint', '--format', 'json', '.']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 500, f"Memory usage too high: {memory_increase:.2f}MB increase"
    
    def test_memory_usage_during_syntax_check(self, project_root):
        """Monitor memory usage during syntax checking"""
        import psutil
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        cmd = [
            'ansible-playbook',
            '--syntax-check',
            '--inventory', str(project_root / 'inventories' / 'dev' / 'hosts.yml'),
            'site.yml'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 200, f"Memory usage too high: {memory_increase:.2f}MB increase"


class TestPerformanceReporting:
    """Generate performance reports"""
    
    def test_generate_performance_report(self, project_root):
        """Generate a comprehensive performance report"""
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'project_stats': {},
            'performance_metrics': {}
        }
        
        # Collect project statistics
        roles_dir = project_root / 'roles'
        role_count = len([d for d in roles_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
        
        playbooks_dir = project_root / 'playbooks'
        playbook_count = len(list(playbooks_dir.glob('*.yml'))) if playbooks_dir.exists() else 0
        
        report_data['project_stats'] = {
            'role_count': role_count,
            'playbook_count': playbook_count,
            'total_files': len(list(project_root.rglob('*.yml')))
        }
        
        # Save report
        report_file = project_root / 'reports' / 'performance_report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Performance report saved to {report_file}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
