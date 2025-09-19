
# HX LiteLLM Proxy Standardized Role

## Description

Enterprise-grade Ansible role for LiteLLM proxy installation and configuration. This role implements comprehensive multi-provider LLM support, database integration, load balancing, and security hardening following SOLID principles and industry best practices.

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, Google, Azure, AWS Bedrock, and more
- **Database Integration**: PostgreSQL backend for logging, caching, and analytics
- **Load Balancing**: Intelligent request routing and failover mechanisms
- **Security Hardening**: API key management, rate limiting, and access controls
- **Performance Optimization**: Caching, connection pooling, and async processing
- **Monitoring**: Built-in metrics, health checks, and observability

## Requirements

- Ansible >= 2.12
- Python >= 3.8
- PostgreSQL >= 12 (for database features)
- Docker (optional, for containerized deployment)
- Minimum 4GB RAM, 20GB disk space

## Role Variables

### Basic Configuration
```yaml
# LiteLLM service configuration
hx_litellm_version: "latest"
hx_litellm_port: 4000
hx_litellm_host: "0.0.0.0"
hx_litellm_workers: 4

# Installation method (pip, docker, source)
hx_litellm_install_method: "pip"
hx_litellm_user: "litellm"
hx_litellm_group: "litellm"
hx_litellm_home: "/opt/litellm"
```

### Database Configuration
```yaml
# Database settings
hx_litellm_database_enabled: true
hx_litellm_database_url: "postgresql://{{ vault_litellm_db_user }}:{{ vault_litellm_db_password }}@localhost:5432/litellm"
hx_litellm_database_pool_size: 10
hx_litellm_database_max_overflow: 20
```

### LLM Provider Configuration
```yaml
# LLM providers configuration
hx_litellm_providers:
  openai:
    enabled: true
    api_key: "{{ vault_openai_api_key }}"
    models:
      - "gpt-4"
      - "gpt-3.5-turbo"
  anthropic:
    enabled: true
    api_key: "{{ vault_anthropic_api_key }}"
    models:
      - "claude-3-opus"
      - "claude-3-sonnet"
```

### Security Configuration
```yaml
# API security
hx_litellm_master_key: "{{ vault_litellm_master_key }}"
hx_litellm_api_keys: []
hx_litellm_rate_limiting_enabled: true
hx_litellm_max_requests_per_minute: 100
```

## Dependencies

- community.postgresql (for database setup)
- community.docker (if using Docker installation)

## Example Playbook

```yaml
- hosts: llm_proxy_servers
  become: yes
  roles:
    - role: hx_litellm_proxy_standardized
      vars:
        hx_litellm_database_enabled: true
        hx_litellm_providers:
          openai:
            enabled: true
            api_key: "{{ vault_openai_api_key }}"
```

## Security Considerations

- All API keys must be stored in Ansible Vault
- Enable rate limiting for production use
- Use SSL/TLS for all external communications
- Regular security audits recommended

## Testing

Run molecule tests:
```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team
