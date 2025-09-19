
#!/usr/bin/env python3
"""
Architecture Diagram Generator for HX Infrastructure Ansible
Creates visual documentation of system architecture and dependencies
"""

import os
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Set, Any
import json


class DiagramGenerator:
    """Generate architecture diagrams for Ansible infrastructure"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.diagrams_dir = self.project_root / "docs_site" / "docs" / "diagrams"
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_role_dependency_graph(self) -> str:
        """Generate role dependency graph using Graphviz"""
        print("🎭 Generating role dependency graph...")
        
        roles_dir = self.project_root / 'roles'
        if not roles_dir.exists():
            return ""
        
        # Collect role dependencies
        dependencies = {}
        roles = []
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                role_name = role_dir.name
                roles.append(role_name)
                dependencies[role_name] = []
                
                meta_file = role_dir / 'meta' / 'main.yml'
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r') as f:
                            meta_data = yaml.safe_load(f) or {}
                            deps = meta_data.get('dependencies', [])
                            
                            for dep in deps:
                                if isinstance(dep, str):
                                    dep_name = dep
                                elif isinstance(dep, dict):
                                    dep_name = dep.get('role', dep.get('name', ''))
                                
                                if dep_name and not dep_name.startswith('community.'):
                                    dependencies[role_name].append(dep_name)
                    except Exception as e:
                        print(f"Warning: Could not parse {meta_file}: {e}")
        
        # Generate DOT file
        dot_content = """digraph RoleDependencies {
    rankdir=TB;
    node [shape=box, style=filled, fillcolor=lightblue];
    edge [color=darkblue];
    
    // Role nodes
"""
        
        for role in roles:
            # Color code different types of roles
            if 'hx_' in role:
                color = 'lightgreen'
            elif 'standardized' in role:
                color = 'lightyellow'
            elif role in ['common', 'operational_safety']:
                color = 'lightcoral'
            else:
                color = 'lightblue'
            
            dot_content += f'    "{role}" [fillcolor={color}];\n'
        
        dot_content += "\n    // Dependencies\n"
        
        for role, deps in dependencies.items():
            for dep in deps:
                if dep in roles:  # Only show internal dependencies
                    dot_content += f'    "{dep}" -> "{role}";\n'
        
        dot_content += "\n    // Legend\n"
        dot_content += '    subgraph cluster_legend {\n'
        dot_content += '        label="Legend";\n'
        dot_content += '        style=filled;\n'
        dot_content += '        fillcolor=white;\n'
        dot_content += '        "HX Roles" [fillcolor=lightgreen];\n'
        dot_content += '        "Standardized" [fillcolor=lightyellow];\n'
        dot_content += '        "Core Roles" [fillcolor=lightcoral];\n'
        dot_content += '        "Other Roles" [fillcolor=lightblue];\n'
        dot_content += '    }\n'
        dot_content += "}\n"
        
        # Save DOT file and generate PNG
        dot_file = self.diagrams_dir / 'role_dependencies.dot'
        png_file = self.diagrams_dir / 'role_dependencies.png'
        
        with open(dot_file, 'w') as f:
            f.write(dot_content)
        
        try:
            subprocess.run([
                'dot', '-Tpng', str(dot_file), '-o', str(png_file)
            ], check=True)
            print(f"✅ Role dependency graph saved to {png_file}")
            return str(png_file)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not generate PNG diagram: {e}")
            return str(dot_file)
    
    def generate_playbook_flow_diagram(self) -> str:
        """Generate playbook execution flow diagram"""
        print("📋 Generating playbook flow diagram...")
        
        # Analyze main site.yml playbook
        site_playbook = self.project_root / 'site.yml'
        if not site_playbook.exists():
            return ""
        
        try:
            with open(site_playbook, 'r') as f:
                playbook_data = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not parse site.yml: {e}")
            return ""
        
        dot_content = """digraph PlaybookFlow {
    rankdir=TB;
    node [shape=rectangle, style=filled];
    edge [color=darkgreen];
    
    // Start node
    start [label="Start Deployment", fillcolor=lightgreen, shape=ellipse];
    
"""
        
        if isinstance(playbook_data, list):
            prev_node = "start"
            
            for i, play in enumerate(playbook_data):
                if isinstance(play, dict) and 'name' in play:
                    play_name = play['name']
                    node_name = f"play_{i}"
                    
                    # Determine node color based on play type
                    if 'security' in play_name.lower():
                        color = 'lightcoral'
                    elif 'backup' in play_name.lower():
                        color = 'lightyellow'
                    elif 'validation' in play_name.lower():
                        color = 'lightblue'
                    else:
                        color = 'lightgray'
                    
                    dot_content += f'    {node_name} [label="{play_name}", fillcolor={color}];\n'
                    dot_content += f'    {prev_node} -> {node_name};\n'
                    
                    # Add roles if present
                    roles = play.get('roles', [])
                    if roles:
                        for j, role in enumerate(roles):
                            role_name = role if isinstance(role, str) else role.get('role', str(role))
                            role_node = f"role_{i}_{j}"
                            dot_content += f'    {role_node} [label="{role_name}", fillcolor=lightsteelblue, shape=box];\n'
                            dot_content += f'    {node_name} -> {role_node};\n'
                    
                    prev_node = node_name
            
            # End node
            dot_content += '    end [label="Deployment Complete", fillcolor=lightgreen, shape=ellipse];\n'
            dot_content += f'    {prev_node} -> end;\n'
        
        dot_content += "}\n"
        
        # Save and generate diagram
        dot_file = self.diagrams_dir / 'playbook_flow.dot'
        png_file = self.diagrams_dir / 'playbook_flow.png'
        
        with open(dot_file, 'w') as f:
            f.write(dot_content)
        
        try:
            subprocess.run([
                'dot', '-Tpng', str(dot_file), '-o', str(png_file)
            ], check=True)
            print(f"✅ Playbook flow diagram saved to {png_file}")
            return str(png_file)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not generate PNG diagram: {e}")
            return str(dot_file)
    
    def generate_infrastructure_overview(self) -> str:
        """Generate high-level infrastructure overview diagram"""
        print("🏗️ Generating infrastructure overview...")
        
        dot_content = """digraph InfrastructureOverview {
    rankdir=TB;
    node [shape=box, style=filled];
    edge [color=darkblue];
    
    // Infrastructure layers
    subgraph cluster_control {
        label="Control Layer";
        style=filled;
        fillcolor=lightblue;
        
        ansible [label="Ansible Controller", fillcolor=lightgreen];
        inventory [label="Dynamic Inventory", fillcolor=lightyellow];
        playbooks [label="Playbooks & Roles", fillcolor=lightcoral];
    }
    
    subgraph cluster_security {
        label="Security Layer";
        style=filled;
        fillcolor=lightcoral;
        
        ca_trust [label="CA Trust Management"];
        domain_join [label="Domain Integration"];
        ssh_keys [label="SSH Key Management"];
        vault [label="Ansible Vault"];
    }
    
    subgraph cluster_services {
        label="Service Layer";
        style=filled;
        fillcolor=lightgreen;
        
        postgresql [label="PostgreSQL Auth"];
        backup [label="Backup Services"];
        monitoring [label="Monitoring"];
        logging [label="Logging"];
    }
    
    subgraph cluster_infrastructure {
        label="Infrastructure Layer";
        style=filled;
        fillcolor=lightyellow;
        
        web_servers [label="Web Servers"];
        db_servers [label="Database Servers"];
        load_balancers [label="Load Balancers"];
        storage [label="Storage Systems"];
    }
    
    // Connections
    ansible -> inventory;
    ansible -> playbooks;
    playbooks -> ca_trust;
    playbooks -> domain_join;
    playbooks -> ssh_keys;
    playbooks -> postgresql;
    playbooks -> backup;
    playbooks -> monitoring;
    
    ca_trust -> web_servers;
    domain_join -> db_servers;
    postgresql -> db_servers;
    backup -> storage;
    monitoring -> web_servers;
    monitoring -> db_servers;
    
    web_servers -> load_balancers;
    db_servers -> storage;
}
"""
        
        # Save and generate diagram
        dot_file = self.diagrams_dir / 'infrastructure_overview.dot'
        png_file = self.diagrams_dir / 'infrastructure_overview.png'
        
        with open(dot_file, 'w') as f:
            f.write(dot_content)
        
        try:
            subprocess.run([
                'dot', '-Tpng', str(dot_file), '-o', str(png_file)
            ], check=True)
            print(f"✅ Infrastructure overview saved to {png_file}")
            return str(png_file)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not generate PNG diagram: {e}")
            return str(dot_file)
    
    def generate_testing_framework_diagram(self) -> str:
        """Generate testing framework architecture diagram"""
        print("🧪 Generating testing framework diagram...")
        
        dot_content = """digraph TestingFramework {
    rankdir=TB;
    node [shape=box, style=filled];
    edge [color=purple];
    
    // Testing layers
    subgraph cluster_unit {
        label="Unit Testing";
        style=filled;
        fillcolor=lightblue;
        
        role_tests [label="Role Structure Tests"];
        variable_tests [label="Variable Validation"];
        syntax_tests [label="Syntax Validation"];
    }
    
    subgraph cluster_integration {
        label="Integration Testing";
        style=filled;
        fillcolor=lightgreen;
        
        deployment_tests [label="Deployment Tests"];
        molecule_tests [label="Molecule Tests"];
        end_to_end [label="End-to-End Tests"];
    }
    
    subgraph cluster_performance {
        label="Performance Testing";
        style=filled;
        fillcolor=lightyellow;
        
        benchmark_tests [label="Benchmark Tests"];
        scalability_tests [label="Scalability Tests"];
        resource_tests [label="Resource Usage"];
    }
    
    subgraph cluster_security {
        label="Security Testing";
        style=filled;
        fillcolor=lightcoral;
        
        vulnerability_scan [label="Vulnerability Scanning"];
        compliance_check [label="Compliance Checking"];
        credential_audit [label="Credential Audit"];
    }
    
    subgraph cluster_chaos {
        label="Chaos Engineering";
        style=filled;
        fillcolor=lightpink;
        
        failure_simulation [label="Failure Simulation"];
        resilience_tests [label="Resilience Tests"];
        recovery_tests [label="Recovery Tests"];
    }
    
    // CI/CD Pipeline
    ci_pipeline [label="CI/CD Pipeline", fillcolor=orange, shape=ellipse];
    
    // Connections
    ci_pipeline -> role_tests;
    ci_pipeline -> deployment_tests;
    ci_pipeline -> benchmark_tests;
    ci_pipeline -> vulnerability_scan;
    ci_pipeline -> failure_simulation;
    
    role_tests -> variable_tests;
    variable_tests -> syntax_tests;
    
    deployment_tests -> molecule_tests;
    molecule_tests -> end_to_end;
    
    benchmark_tests -> scalability_tests;
    scalability_tests -> resource_tests;
    
    vulnerability_scan -> compliance_check;
    compliance_check -> credential_audit;
    
    failure_simulation -> resilience_tests;
    resilience_tests -> recovery_tests;
}
"""
        
        # Save and generate diagram
        dot_file = self.diagrams_dir / 'testing_framework.dot'
        png_file = self.diagrams_dir / 'testing_framework.png'
        
        with open(dot_file, 'w') as f:
            f.write(dot_content)
        
        try:
            subprocess.run([
                'dot', '-Tpng', str(dot_file), '-o', str(png_file)
            ], check=True)
            print(f"✅ Testing framework diagram saved to {png_file}")
            return str(png_file)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not generate PNG diagram: {e}")
            return str(dot_file)
    
    def generate_all_diagrams(self) -> Dict[str, str]:
        """Generate all architecture diagrams"""
        print("\n🎨 Generating architecture diagrams...")
        
        diagrams = {}
        
        try:
            diagrams['role_dependencies'] = self.generate_role_dependency_graph()
            diagrams['playbook_flow'] = self.generate_playbook_flow_diagram()
            diagrams['infrastructure_overview'] = self.generate_infrastructure_overview()
            diagrams['testing_framework'] = self.generate_testing_framework_diagram()
        except Exception as e:
            print(f"Error generating diagrams: {e}")
        
        # Generate diagram index
        self.generate_diagram_index(diagrams)
        
        return diagrams
    
    def generate_diagram_index(self, diagrams: Dict[str, str]) -> None:
        """Generate markdown index of all diagrams"""
        index_content = """# Architecture Diagrams

This section contains visual documentation of the HX Infrastructure Ansible architecture.

## Available Diagrams

"""
        
        diagram_descriptions = {
            'role_dependencies': 'Role Dependencies - Shows relationships between Ansible roles',
            'playbook_flow': 'Playbook Flow - Illustrates the execution flow of main playbooks',
            'infrastructure_overview': 'Infrastructure Overview - High-level system architecture',
            'testing_framework': 'Testing Framework - Comprehensive testing architecture'
        }
        
        for diagram_key, diagram_path in diagrams.items():
            if diagram_path:
                description = diagram_descriptions.get(diagram_key, diagram_key.replace('_', ' ').title())
                filename = Path(diagram_path).name
                
                index_content += f"""
### {description}

![{description}](diagrams/{filename})

"""
        
        index_content += """
## Diagram Generation

These diagrams are automatically generated from the Ansible infrastructure code using:

- **Graphviz** for dependency and flow diagrams
- **Role metadata** for dependency analysis
- **Playbook structure** for flow visualization
- **Testing framework** for test architecture

To regenerate diagrams:

```bash
python scripts/quality/generate_diagrams.py
```

## Legend

- **Green nodes**: Entry points and successful states
- **Blue nodes**: Standard components and processes
- **Yellow nodes**: Configuration and data components
- **Red nodes**: Security and critical components
- **Pink nodes**: Testing and validation components

"""
        
        index_file = self.diagrams_dir.parent / 'architecture' / 'diagrams.md'
        index_file.parent.mkdir(exist_ok=True)
        
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        print(f"📋 Diagram index saved to {index_file}")


def main():
    """Main execution function"""
    generator = DiagramGenerator()
    diagrams = generator.generate_all_diagrams()
    
    print(f"\n✅ Generated {len(diagrams)} architecture diagrams")
    for name, path in diagrams.items():
        if path:
            print(f"  - {name}: {path}")
    
    return diagrams


if __name__ == '__main__':
    main()
