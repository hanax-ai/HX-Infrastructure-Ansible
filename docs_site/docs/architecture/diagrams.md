# Architecture Diagrams

This section contains visual documentation of the HX Infrastructure Ansible architecture.

## Available Diagrams


### Role Dependencies - Shows relationships between Ansible roles

![Role Dependencies - Shows relationships between Ansible roles](diagrams/role_dependencies.png)


### Playbook Flow - Illustrates the execution flow of main playbooks

![Playbook Flow - Illustrates the execution flow of main playbooks](diagrams/playbook_flow.png)


### Infrastructure Overview - High-level system architecture

![Infrastructure Overview - High-level system architecture](diagrams/infrastructure_overview.png)


### Testing Framework - Comprehensive testing architecture

![Testing Framework - Comprehensive testing architecture](diagrams/testing_framework.png)


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

