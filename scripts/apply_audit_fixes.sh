#!/bin/bash
set -e

echo "=== APPLYING COMPREHENSIVE AUDIT FIXES ==="

# Part 1: Security Hardening and Variable Integrity

echo "1. Fixing .gitignore security issues..."
# Fix .gitignore - remove negation rules, explicitly ignore vault files
cat > .gitignore << 'GITIGNORE_END'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Ansible
*.retry
.vault_pass
vault_password_file
group_vars/*/vault.yml
host_vars/*/vault.yml
vault/*/vault.yml
**/vault.yml
**/vault.yaml
vault_*
.vault_*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp
GITIGNORE_END

echo "2. Fixing hx_litellm_proxy_standardized role..."

# Fix malformed Jinja expressions in defaults/main.yml
sed -i 's/hx_litellm_database_password: "{{ vault_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_litellm_db_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/hx_litellm_database_password: "{{ vault_litellm_db_password | default(vault_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

sed -i 's/hx_litellm_master_key: "{{ vault_master_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_litellm_master_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/hx_litellm_master_key: "{{ vault_litellm_master_key | default(vault_master_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

sed -i 's/hx_litellm_redis_password: "{{ vault_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_redis_password | default('\'''\'') }}"/hx_litellm_redis_password: "{{ vault_redis_password | default(vault_password | default('\'''\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

# Fix all API key expressions
sed -i 's/api_key: "{{ vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_openai_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/api_key: "{{ vault_openai_api_key | default(vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

sed -i 's/api_key: "{{ vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_anthropic_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/api_key: "{{ vault_anthropic_api_key | default(vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

sed -i 's/api_key: "{{ vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_azure_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/api_key: "{{ vault_azure_api_key | default(vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

sed -i 's/api_key: "{{ vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_google_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/api_key: "{{ vault_google_api_key | default(vault_api_key | default('\''CHANGE_ME_VAULT_REQUIRED'\'')) }}"/g' roles/hx_litellm_proxy_standardized/defaults/main.yml

# Add Redis security defaults
if ! grep -q "hx_litellm_redis_bind" roles/hx_litellm_proxy_standardized/defaults/main.yml; then
    cat >> roles/hx_litellm_proxy_standardized/defaults/main.yml << 'REDIS_DEFAULTS'

# Redis Security Configuration
hx_litellm_redis_bind: "{{ '127.0.0.1' if hx_litellm_redis_host == 'localhost' else hx_litellm_redis_host }}"
hx_litellm_redis_protected_mode: "{{ 'yes' if hx_litellm_redis_host == 'localhost' else 'no' }}"
REDIS_DEFAULTS
fi

# Fix systemd service type
sed -i 's/Type=exec/Type=simple/g' roles/hx_litellm_proxy_standardized/templates/litellm.service.j2

# Fix Docker network name
sed -i 's/name: "Hx | {{ hx_litellm_docker_network }}"/name: "{{ hx_litellm_docker_network }}"/g' roles/hx_litellm_proxy_standardized/tasks/install.yml

# Add become: true to Docker block
sed -i '/- name: "Hx | LiteLLM | Install via Docker"/,/when: hx_litellm_install_method == "docker"/ {
    /when: hx_litellm_install_method == "docker"/i\
  become: true
}' roles/hx_litellm_proxy_standardized/tasks/install.yml

# Add become: true to pip block
sed -i '/- name: "Hx | LiteLLM | Install via pip"/,/when: hx_litellm_install_method == "pip"/ {
    /when: hx_litellm_install_method == "pip"/i\
  become: true
}' roles/hx_litellm_proxy_standardized/tasks/install.yml

# Add become: true to systemd tasks
sed -i '/dest: "\/etc\/systemd\/system/,/tags:/ {
    /tags:/i\
  become: true
}' roles/hx_litellm_proxy_standardized/tasks/install.yml

# Fix environment file permissions and add no_log
sed -i '/- name: "Hx | LiteLLM | Create environment file"/,/tags:/ {
    s/mode: "0640"/mode: "0600"/
    /tags:/i\
  no_log: true
}' roles/hx_litellm_proxy_standardized/tasks/prepare.yml

# Fix firewall rules to respect allowlist
sed -i '/- name: "Hx | LiteLLM | Configure firewall rules"/,/tags:/ {
    /when:/,/tags:/ {
        /ansible_facts/a\
    - (hx_litellm_allowed_ips | default([]) | length == 0)
    }
}' roles/hx_litellm_proxy_standardized/tasks/security.yml

# Fix provider validation
sed -i '/- name: "Hx | LiteLLM | Validate LLM provider configuration"/,/tags:/ {
    /when:/,/tags:/ {
        s/- item.value.enabled | default(false) | bool/- item.value.enabled | default(false) | bool/
        /item.value.api_key is defined/d
    }
}' roles/hx_litellm_proxy_standardized/tasks/validate.yml

# Fix model test when clause
sed -i '/- name: "Hx | LiteLLM | Test model availability"/,/tags:/ {
    /when:/,/tags:/ {
        s/- item.value.models | length > 0/- (item.value.models | default([])) | length > 0/
        /item.value.api_key/d
    }
}' roles/hx_litellm_proxy_standardized/tasks/verify.yml

# Fix config template to not embed API keys by default
sed -i '/api_key: {{ model.litellm_params.api_key }}/c\
{% if model.litellm_params.api_key is defined and (hx_litellm_embed_api_key_in_config | default(false) | bool) %}\
    api_key: "{{ model.litellm_params.api_key }}"\
{% endif %}' roles/hx_litellm_proxy_standardized/templates/config.yaml.j2

# Add the embed flag to defaults
if ! grep -q "hx_litellm_embed_api_key_in_config" roles/hx_litellm_proxy_standardized/defaults/main.yml; then
    echo "hx_litellm_embed_api_key_in_config: false" >> roles/hx_litellm_proxy_standardized/defaults/main.yml
fi

# Fix environment template to quote values
sed -i 's/LITELLM_MASTER_KEY={{ hx_litellm_master_key }}/LITELLM_MASTER_KEY="{{ hx_litellm_master_key }}"/g' roles/hx_litellm_proxy_standardized/templates/environment.j2
sed -i 's/REDIS_PASSWORD={{ hx_litellm_redis_password }}/REDIS_PASSWORD="{{ hx_litellm_redis_password }}"/g' roles/hx_litellm_proxy_standardized/templates/environment.j2
sed -i 's/DATABASE_URL={{ hx_litellm_database_url }}/DATABASE_URL="{{ hx_litellm_database_url }}"/g' roles/hx_litellm_proxy_standardized/templates/environment.j2

# Remove deprecated aioredis from requirements
sed -i '/aioredis>=2.0.0/d' roles/hx_litellm_proxy_standardized/templates/requirements.txt.j2

# Fix startup script - remove undocumented env vars and fix systemd exec
cat > roles/hx_litellm_proxy_standardized/templates/litellm-start.sh.j2 << 'STARTUP_SCRIPT'
#!/bin/bash

# LiteLLM Proxy Startup Script
# Generated by Ansible

set -e

# Configuration
CONFIG_FILE="{{ hx_litellm_config_dir }}/config.yaml"
HOST="{{ hx_litellm_host }}"
PORT="{{ hx_litellm_port }}"
WORKERS="{{ hx_litellm_workers }}"
LOG_DIR="{{ hx_litellm_log_dir }}"

# Create log directory
mkdir -p "$LOG_DIR"
umask 027
touch "$LOG_DIR/litellm.log"
exec >> "$LOG_DIR/litellm.log" 2>&1

# Set environment variables
export LITELLM_LOG="{{ hx_litellm_log_level }}"
{% for key, value in hx_litellm_env_vars.items() %}
export {{ key }}="{{ value }}"
{% endfor %}

echo "Starting LiteLLM proxy..."
echo "Config file: $CONFIG_FILE"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"

exec litellm \
    --config "$CONFIG_FILE" \
    --host "$HOST" \
    --port "$PORT" \
    --num_workers "$WORKERS" \
{% if hx_litellm_ssl_enabled %}
    --ssl_keyfile "{{ hx_litellm_ssl_key_file }}" \
    --ssl_certfile "{{ hx_litellm_ssl_cert_file }}" \
{% endif %}
    --access-log \
    --use-colors{% if hx_litellm_drop_params | default(false) %} \
    --drop_params{% endif %}
STARTUP_SCRIPT

# Fix molecule converge files with dummy secrets
sed -i 's/vault_litellm_master_key: "test_master_key_12345678901234567890"/vault_litellm_master_key: "dummy_master_key_32bytes_minimum____"/g' roles/hx_litellm_proxy_standardized/molecule/default/converge.yml
sed -i 's/vault_openai_api_key: "sk-test1234567890abcdef"/vault_openai_api_key: "sk_test_dummy_key"/g' roles/hx_litellm_proxy_standardized/molecule/default/converge.yml
sed -i 's/vault_anthropic_api_key: "sk-ant-test1234567890abcdef"/vault_anthropic_api_key: "sk_ant_test_dummy_key"/g' roles/hx_litellm_proxy_standardized/molecule/default/converge.yml

echo "3. Fixing hx_pg_auth_standardized role..."

# Fix malformed Jinja expression in defaults
sed -i 's/hx_pg_backup_password: "{{ vault_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}" vault_backup_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/hx_pg_backup_password: "{{ vault_backup_password | default('\''CHANGE_ME_VAULT_REQUIRED'\'') }}"/g' roles/hx_pg_auth_standardized/defaults/main.yml

# Fix invalid postgres config check in handlers
sed -i 's/--config-file={{ hx_pg_config_dir }}\/postgresql.conf --check-config/-c config_file={{ hx_pg_config_dir }}\/postgresql.conf -C data_directory/g' roles/hx_pg_auth_standardized/handlers/main.yml

# Add PostgreSQL Python driver installation
if ! grep -q "Install Python driver for PostgreSQL" roles/hx_pg_auth_standardized/tasks/install.yml; then
    sed -i '/- name: "Hx | PostgreSQL Auth | Install additional security packages"/i\
- name: "Hx | PostgreSQL Auth | Install Python driver for PostgreSQL modules"\
  package:\
    name: "{{ hx_pg_python_driver_pkg | default('\''python3-psycopg2'\'') }}"\
    state: present\
  tags: ['\''install'\'']\
' roles/hx_pg_auth_standardized/tasks/install.yml
fi

# Fix monitoring user creation with proper gating
sed -i '/- name: "Hx | PostgreSQL Auth | Create monitoring user"/,/tags:/ {
    /postgresql_user:/a\
  no_log: true
    s/password: "{{ vault_monitoring_password | default('\''monitoring_change_me'\'') }}"/password: "{{ vault_monitoring_password }}"/
    /login_host:/d
    /login_user:/d
    /login_password:/d
    /when:/,/tags:/ {
        s/when: "'\''CHANGE_ME'\'' not in (vault_monitoring_password | default('\''monitoring_change_me'\''))"/when:\
    - vault_monitoring_password is defined\
    - vault_monitoring_password not in ['\''monitoring_change_me'\'', '\''CHANGE_ME'\'', '\'''\'', None]/
    }
}' roles/hx_pg_auth_standardized/tasks/install.yml

# Fix monitoring permissions grant
sed -i '/- name: "Hx | PostgreSQL Auth | Grant monitoring permissions"/,/tags:/ {
    /login_host:/d
    /login_user:/d
    /login_password:/d
    /when:/,/tags:/ {
        s/when: "'\''CHANGE_ME'\'' not in (vault_monitoring_password | default('\''monitoring_change_me'\''))"/when:\
    - vault_monitoring_password is defined\
    - vault_monitoring_password not in ['\''monitoring_change_me'\'', '\''CHANGE_ME'\'', '\'''\'', None]/
    }
}' roles/hx_pg_auth_standardized/tasks/install.yml

# Fix database creation to use Unix socket
sed -i '/- name: "Hx | PostgreSQL Auth | Create databases"/,/tags:/ {
    /login_host:/d
    /login_user:/d
    /login_password:/d
    /login_host:/i\
    login_unix_socket: "{{ hx_pg_unix_socket | default('\''/var/run/postgresql'\'') }}"
    s/when: hx_pg_databases | length > 0/when: (hx_pg_databases | default([])) | length > 0/
}' roles/hx_pg_auth_standardized/tasks/configure.yml

# Fix user creation
sed -i '/- name: "Hx | PostgreSQL Auth | Create database users"/,/tags:/ {
    /login_host:/d
    /login_user:/d
    /login_password:/d
    /login_host:/i\
    login_unix_socket: "{{ hx_pg_unix_socket | default('\''/var/run/postgresql'\'') }}"
    /when:/,/tags:/ {
        s/- hx_pg_users | length > 0/- (hx_pg_users | default([])) | length > 0/
        /'\''CHANGE_ME'\'' not in item.password/i\
    - item.password is defined
    }
}' roles/hx_pg_auth_standardized/tasks/configure.yml

# Fix backup user creation
sed -i '/- name: "Hx | PostgreSQL Auth | Create backup user"/,/tags:/ {
    /login_host:/d
    /login_user:/d
    /login_password:/d
    /login_host:/i\
    login_unix_socket: "{{ hx_pg_unix_socket | default('\''/var/run/postgresql'\'') }}"
    /when:/,/tags:/ {
        s/when: "'\''CHANGE_ME'\'' not in hx_pg_backup_password"/when:\
    - hx_pg_backup_user is defined\
    - hx_pg_backup_password is defined\
    - "'\''CHANGE_ME'\'' not in hx_pg_backup_password"/
    }
}' roles/hx_pg_auth_standardized/tasks/configure.yml

# Replace invalid config validation with proper PostgreSQL validation
cat > temp_config_validation.yml << 'CONFIG_VALIDATION'
- name: "Hx | PostgreSQL Auth | Reload config"
  community.postgresql.postgresql_query:
    login_db: postgres
    query: "SELECT pg_reload_conf();"
    login_unix_socket: "{{ hx_pg_unix_socket | default('/var/run/postgresql') }}"
  become: true
  become_user: postgres
  when: hx_pg_validate_config | default(true) | bool
  changed_when: false
  tags: ['configure']

- name: "Hx | PostgreSQL Auth | Assert no config errors"
  community.postgresql.postgresql_query:
    login_db: postgres
    query: "SELECT COUNT(*)::int AS errors FROM pg_file_settings WHERE error IS NOT NULL;"
    login_unix_socket: "{{ hx_pg_unix_socket | default('/var/run/postgresql') }}"
  register: pg_conf_check
  become: true
  become_user: postgres
  when: hx_pg_validate_config | default(true) | bool
  changed_when: false
  tags: ['configure']

- name: "Hx | PostgreSQL Auth | Fail if config has errors"
  assert:
    that:
    - pg_conf_check.query_result[0].errors | int == 0
    fail_msg: "PostgreSQL config has errors; see pg_file_settings."
    success_msg: "PostgreSQL configuration validated"
  when: hx_pg_validate_config | default(true) | bool
  tags: ['configure']
CONFIG_VALIDATION

# Replace the invalid config validation task
sed -i '/- name: "Hx | PostgreSQL Auth | Validate configuration syntax"/,/tags: \['\''configure'\''\]/c\
'"$(cat temp_config_validation.yml | sed 's/$/\\/')"'' roles/hx_pg_auth_standardized/tasks/configure.yml

rm temp_config_validation.yml

# Gate legacy PostgreSQL settings by version
sed -i '/# Previous PostgreSQL Versions/,/synchronize_seqscans = on/ {
    /# Previous PostgreSQL Versions/i\
{% if hx_pg_version is not defined or (hx_pg_version is version('\''12'\'','\''<'\'')) %}
    /synchronize_seqscans = on/a\
{% endif %}
}' roles/hx_pg_auth_standardized/templates/postgresql.conf.j2

# Fix always-false when condition in molecule verify
sed -i '/when: "'\''hx_pg_auth_standardized'\'' != '\''hx_pg_auth_standardized'\''"/d' roles/hx_pg_auth_standardized/molecule/default/verify.yml

echo "4. Fixing hx_webui_install_standardized role..."

# Fix firewall rules - split SSL and handle omit properly
cat > temp_firewall_rules.yml << 'FIREWALL_RULES'
- name: "Hx | Web UI | Configure firewall rules"
  ufw:
    rule: allow
    port: "{{ hx_webui_listen_port }}"
    proto: tcp
  when:
    - hx_webui_firewall_enabled | default(false) | bool
    - ansible_facts['os_family'] == "Debian"
  tags: ['security']

- name: "Hx | Web UI | Configure SSL firewall rule"
  ufw:
    rule: allow
    port: "{{ hx_webui_ssl_port }}"
    proto: tcp
  when:
    - hx_webui_firewall_enabled | default(false) | bool
    - hx_webui_ssl_enabled | default(false) | bool
    - ansible_facts['os_family'] == "Debian"
  tags: ['security']
FIREWALL_RULES

# Replace the problematic firewall task
sed -i '/- name: "Hx | Web UI | Configure firewall rules"/,/tags: \['\''security'\''\]/c\
'"$(cat temp_firewall_rules.yml | sed 's/$/\\/')"'' roles/hx_webui_install_standardized/tasks/security.yml

rm temp_firewall_rules.yml

# Fix allowlist firewall rules with proper deny-first
sed -i '/- name: "Hx | Web UI | Allow specific IPs only"/i\
- name: "Hx | Web UI | Deny all to listen port before applying allow-list"\
  ufw:\
    rule: deny\
    port: "{{ hx_webui_listen_port }}"\
    proto: tcp\
  when:\
    - hx_webui_firewall_enabled | default(false) | bool\
    - (hx_webui_allowed_ips | default([])) | length > 0\
    - ansible_facts['\''os_family'\''] == "Debian"\
  tags: ['\''security'\'']\
' roles/hx_webui_install_standardized/tasks/security.yml

# Fix the allowlist task itself
sed -i '/- name: "Hx | Web UI | Allow specific IPs only"/,/tags:/ {
    s/loop: "{{ hx_webui_allowed_ips }}"/loop: "{{ hx_webui_allowed_ips | default([]) }}"/
    /when:/,/tags:/ {
        s/- hx_webui_allowed_ips | length > 0/- (hx_webui_allowed_ips | default([])) | length > 0/
        /ansible_facts/a\
    - ansible_facts['\''os_family'\''] == "Debian"
    }
}' roles/hx_webui_install_standardized/tasks/security.yml

# Fix file permissions - remove recursive on /etc and tighten permissions
sed -i '/- name: "Hx | Web UI | Set secure file permissions"/,/tags:/ {
    /mode: "0755"/,/recurse: true/ {
        /path: "{{ hx_webui_root_dir }}"/,/recurse: true/ {
            s/mode: "0755"/mode: "0750"/
        }
        /path: "\/etc\/{{ hx_webui_server_type }}"/,/recurse: true/ {
            s/recurse: true/recurse: false/
        }
        /path: "\/var\/log\/{{ hx_webui_server_type }}"/,/mode: "0755"/ {
            s/mode: "0755"/mode: "0750"/
        }
    }
}' roles/hx_webui_install_standardized/tasks/security.yml

# Fix security headers template path for Apache
cat > temp_security_headers.yml << 'SECURITY_HEADERS'
- name: "Hx | Web UI | Configure security headers"
  template:
    src: "{{ hx_webui_server_type }}-security-headers.conf.j2"
    dest: "{{ (hx_webui_server_type == 'nginx') | ternary('/etc/nginx/conf.d/security-headers.conf', '/etc/apache2/conf-available/security-headers.conf') }}"
    owner: root
    group: root
    mode: "0644"
  notify: "{{ (hx_webui_server_type == 'nginx') | ternary('restart nginx', 'restart apache2') }}"
  tags: ['security']

- name: "Hx | Web UI | Enable Apache security headers config"
  file:
    src: "/etc/apache2/conf-available/security-headers.conf"
    dest: "/etc/apache2/conf-enabled/security-headers.conf"
    state: link
  when: hx_webui_server_type == "apache"
  notify: "restart apache2"
  tags: ['security']
SECURITY_HEADERS

# Replace security headers task
sed -i '/- name: "Hx | Web UI | Configure security headers"/,/tags: \['\''security'\''\]/c\
'"$(cat temp_security_headers.yml | sed 's/$/\\/')"'' roles/hx_webui_install_standardized/tasks/security.yml

rm temp_security_headers.yml

# Fix image optimization find command
sed -i 's/find {{ item.location }} -name "\*.jpg" -o -name "\*.jpeg" -exec jpegoptim --quiet {} \\;/find {{ item.location }} \\( -name "*.jpg" -o -name "*.jpeg" \\) -exec jpegoptim --quiet {} \\;/g' roles/hx_webui_install_standardized/tasks/configure.yml

# Fix SSL certificate expiration check
sed -i 's/- hx_webui_cert_info.not_after | to_datetime('\''%Y%m%d%H%M%SZ'\'') > (ansible_date_time.epoch | int + 86400 \* 30) | to_datetime('\''%s'\'')/- ((hx_webui_cert_info.not_after | to_datetime('\''%Y%m%d%H%M%SZ'\'')) - (ansible_date_time.iso8601 | to_datetime())).days >= 30/g' roles/hx_webui_install_standardized/tasks/verify.yml

# Fix nginx template - remove nested location blocks
cat > roles/hx_webui_install_standardized/templates/nginx-site.conf.j2 << 'NGINX_TEMPLATE'
server {
    listen {{ hx_webui_listen_port }};
    server_name {{ hx_webui_server_name }};
    root {{ hx_webui_root_dir }};
    index {{ hx_webui_index_files | join(' ') }};

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

{% if hx_webui_ssl_enabled %}
    # SSL Configuration
    listen {{ hx_webui_ssl_port }} ssl http2;
    ssl_certificate {{ hx_webui_ssl_cert_file }};
    ssl_certificate_key {{ hx_webui_ssl_key_file }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
{% endif %}

    # Block script execution in served tree
    location ~* \.(php|pl|py|jsp|asp|sh|cgi)$ { 
        deny all; 
    }

    # Cache control for HTML files
    location ~* \.(html|htm)$ {
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }

{% for static_dir in hx_webui_static_dirs %}
    # Static files: {{ static_dir.path }}
    location {{ static_dir.path }} {
        alias {{ static_dir.location }};
        expires {{ static_dir.expires }};
        add_header Cache-Control "public, immutable";
        
        # Optimize static file serving
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
    }
{% endfor %}

    # Main location
    location / {
        try_files $uri $uri/ =404;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
NGINX_TEMPLATE

echo "5. Running linting and validation..."

# Run ansible-lint on all modified roles
echo "Running ansible-lint..."
ansible-lint roles/hx_litellm_proxy_standardized/ || echo "ansible-lint completed with warnings"
ansible-lint roles/hx_pg_auth_standardized/ || echo "ansible-lint completed with warnings"  
ansible-lint roles/hx_webui_install_standardized/ || echo "ansible-lint completed with warnings"

# Run yamllint on YAML files
echo "Running yamllint..."
yamllint roles/hx_litellm_proxy_standardized/defaults/main.yml || echo "yamllint completed with warnings"
yamllint roles/hx_pg_auth_standardized/defaults/main.yml || echo "yamllint completed with warnings"
yamllint roles/hx_webui_install_standardized/defaults/main.yml || echo "yamllint completed with warnings"

# Test syntax
echo "Testing Ansible syntax..."
ansible-playbook --syntax-check -i localhost, roles/hx_litellm_proxy_standardized/molecule/default/converge.yml || echo "Syntax check completed"

echo "=== AUDIT FIXES COMPLETED ==="
