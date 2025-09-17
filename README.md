
# HX Infrastructure Ansible

## 🚀 Enterprise Infrastructure Automation Platform

A comprehensive Ansible-based infrastructure automation platform designed for scalable, secure, and maintainable enterprise deployments.

### 📋 Project Overview

This repository contains a complete infrastructure automation solution built with Ansible, featuring:

- **15-Server Architecture**: Comprehensive multi-tier infrastructure setup
- **Phase-Based Development**: Structured 4-phase implementation approach
- **Visual Documentation**: Extensive Mermaid diagrams for all components
- **Security-First Design**: Integrated secrets management and security controls
- **CI/CD Integration**: Automated testing and deployment pipelines

### 🏗️ Infrastructure Architecture

```mermaid
graph TB
    subgraph "Load Balancer Tier"
        LB1[Load Balancer 1<br/>nginx + keepalived]
        LB2[Load Balancer 2<br/>nginx + keepalived]
    end
    
    subgraph "Web Tier"
        WEB1[Web Server 1<br/>nginx + app]
        WEB2[Web Server 2<br/>nginx + app]
        WEB3[Web Server 3<br/>nginx + app]
    end
    
    subgraph "Application Tier"
        APP1[App Server 1<br/>application runtime]
        APP2[App Server 2<br/>application runtime]
        APP3[App Server 3<br/>application runtime]
    end
    
    subgraph "Database Tier"
        DB1[Database Master<br/>PostgreSQL/MySQL]
        DB2[Database Replica 1<br/>read replica]
        DB3[Database Replica 2<br/>read replica]
    end
    
    subgraph "Cache Tier"
        CACHE1[Redis Master]
        CACHE2[Redis Replica]
    end
    
    subgraph "Monitoring & Management"
        MON1[Monitoring Server<br/>Prometheus + Grafana]
        LOG1[Log Server<br/>ELK Stack]
    end
    
    LB1 --> WEB1
    LB1 --> WEB2
    LB1 --> WEB3
    LB2 --> WEB1
    LB2 --> WEB2
    LB2 --> WEB3
    
    WEB1 --> APP1
    WEB2 --> APP2
    WEB3 --> APP3
    
    APP1 --> DB1
    APP2 --> DB1
    APP3 --> DB1
    
    DB1 --> DB2
    DB1 --> DB3
    
    APP1 --> CACHE1
    APP2 --> CACHE1
    APP3 --> CACHE1
    
    CACHE1 --> CACHE2
    
    MON1 -.-> LB1
    MON1 -.-> LB2
    MON1 -.-> WEB1
    MON1 -.-> WEB2
    MON1 -.-> WEB3
    MON1 -.-> APP1
    MON1 -.-> APP2
    MON1 -.-> APP3
    MON1 -.-> DB1
    MON1 -.-> DB2
    MON1 -.-> DB3
    MON1 -.-> CACHE1
    MON1 -.-> CACHE2
    
    LOG1 -.-> LB1
    LOG1 -.-> LB2
    LOG1 -.-> WEB1
    LOG1 -.-> WEB2
    LOG1 -.-> WEB3
    LOG1 -.-> APP1
    LOG1 -.-> APP2
    LOG1 -.-> APP3
```

### 🎯 Development Phases

```mermaid
gantt
    title HX Infrastructure Development Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1.0
    Foundation Setup           :done, phase1, 2025-09-17, 1d
    Documentation Framework    :done, docs1, 2025-09-17, 1d
    Directory Structure        :done, struct1, 2025-09-17, 1d
    
    section Phase 2.0
    Core Playbooks            :phase2, after phase1, 3d
    Basic Roles               :roles2, after phase1, 3d
    Testing Framework         :test2, after roles2, 2d
    
    section Phase 3.0
    Advanced Features         :phase3, after test2, 5d
    Security Hardening        :sec3, after phase3, 3d
    Performance Optimization  :perf3, after sec3, 2d
    
    section Phase 4.0
    Production Deployment     :phase4, after perf3, 3d
    Monitoring Integration    :mon4, after phase4, 2d
    Documentation Finalization :docs4, after mon4, 1d
```

### 📁 Directory Structure

```
HX-Infrastructure-Ansible/
├── 📁 playbooks/                    # Main Ansible playbooks
│   ├── 📁 site/                     # Site-wide playbooks
│   ├── 📁 services/                 # Service-specific playbooks
│   ├── 📁 maintenance/              # Maintenance and operations
│   └── 📁 deployment/               # Deployment workflows
├── 📁 roles/                        # Ansible roles
│   ├── 📁 common/                   # Common system configurations
│   ├── 📁 web/                      # Web server roles
│   ├── 📁 database/                 # Database roles
│   ├── 📁 monitoring/               # Monitoring and logging
│   └── 📁 security/                 # Security hardening
├── 📁 inventory/                    # Inventory management
│   ├── 📁 environments/             # Environment-specific configs
│   ├── 📁 group_vars/               # Group variables
│   └── 📁 host_vars/                # Host-specific variables
├── 📁 vars/                         # Variable definitions
├── 📁 templates/                    # Jinja2 templates
├── 📁 files/                        # Static files
├── 📁 scripts/                      # Utility scripts
├── 📁 tests/                        # Testing framework
├── 📁 docs/                         # Documentation
└── 📁 .github/                      # GitHub workflows
```

### 🔧 Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/hanax-ai/HX-Infrastructure-Ansible.git
   cd HX-Infrastructure-Ansible
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ansible-galaxy install -r requirements.yml
   ```

3. **Configure Inventory**
   ```bash
   cp inventory/environments/example inventory/environments/production
   # Edit inventory/environments/production/hosts.yml
   ```

4. **Run Site Playbook**
   ```bash
   ansible-playbook -i inventory/environments/production playbooks/site/main.yml
   ```

### 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Detailed system architecture
- [Development Guide](docs/DEVELOPMENT_GUIDE.md) - Development workflows
- [User Guide](docs/USER_GUIDE.md) - Usage instructions
- [API Reference](docs/API_REFERENCE.md) - Ansible role APIs

### 🔒 Security

- Ansible Vault for secrets management
- Role-based access control (RBAC)
- Security hardening playbooks
- Compliance automation (CIS, NIST)

### 🧪 Testing

- Molecule for role testing
- CI/CD pipeline integration
- Infrastructure validation
- Performance benchmarking

### 📊 Monitoring

- Prometheus metrics collection
- Grafana dashboards
- ELK stack for logging
- Alerting and notifications

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the [documentation](docs/)
- Review existing [discussions](https://github.com/hanax-ai/HX-Infrastructure-Ansible/discussions)

---

**Note**: For GitHub App permissions to access private repositories, please visit: [GitHub App Installation](https://github.com/apps/abacusai/installations/select_target)
