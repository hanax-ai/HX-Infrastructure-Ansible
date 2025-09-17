
# HX Web UI Install Standardized Role

## Description

Enterprise-grade Ansible role for web UI installation and configuration. This role implements comprehensive web server setup, SSL/TLS configuration, static file management, and security hardening following SOLID principles and industry best practices.

## Features

- **Multi-Server Support**: Nginx, Apache, and custom web server configurations
- **SSL/TLS Management**: Automated certificate management and security headers
- **Static File Optimization**: Asset optimization, compression, and CDN integration
- **Security Hardening**: Web application firewall, security headers, and access controls
- **Performance Optimization**: Caching, compression, and load balancing support
- **Health Monitoring**: Built-in health checks and monitoring integration

## Requirements

- Ansible >= 2.12
- Ubuntu 20.04+ or Debian 11+
- SSL certificates (for HTTPS)
- Minimum 2GB RAM, 10GB disk space

## Role Variables

### Web Server Configuration
```yaml
# Web server type (nginx, apache, custom)
hx_webui_server_type: "nginx"

# Server configuration
hx_webui_server_name: "{{ ansible_fqdn }}"
hx_webui_listen_port: 80
hx_webui_ssl_port: 443
hx_webui_root_dir: "/var/www/html"

# Application configuration
hx_webui_app_name: "hx-webui"
hx_webui_app_version: "latest"
hx_webui_app_user: "www-data"
hx_webui_app_group: "www-data"
```

### SSL/TLS Configuration
```yaml
# SSL configuration
hx_webui_ssl_enabled: true
hx_webui_ssl_cert_file: "/etc/ssl/certs/webui.crt"
hx_webui_ssl_key_file: "/etc/ssl/private/webui.key"
hx_webui_ssl_protocols: "TLSv1.2 TLSv1.3"
hx_webui_ssl_ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"

# Security headers
hx_webui_security_headers:
  - "X-Frame-Options: DENY"
  - "X-Content-Type-Options: nosniff"
  - "X-XSS-Protection: 1; mode=block"
  - "Strict-Transport-Security: max-age=31536000; includeSubDomains"
```

### Performance Configuration
```yaml
# Caching configuration
hx_webui_enable_caching: true
hx_webui_cache_max_age: 86400
hx_webui_enable_gzip: true
hx_webui_gzip_types: "text/plain text/css application/json application/javascript"

# Static file optimization
hx_webui_optimize_assets: true
hx_webui_minify_css: true
hx_webui_minify_js: true
```

## Dependencies

- geerlingguy.nginx (when using nginx)
- geerlingguy.apache (when using apache)

## Example Playbook

```yaml
- hosts: web_servers
  become: yes
  roles:
    - role: hx_webui_install_standardized
      vars:
        hx_webui_server_type: "nginx"
        hx_webui_ssl_enabled: true
        hx_webui_server_name: "myapp.example.com"
```

## Security Considerations

- SSL certificates must be managed externally
- Regular security updates recommended
- Monitor access logs for suspicious activity
- Implement rate limiting for production use

## Testing

Run molecule tests:
```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team
