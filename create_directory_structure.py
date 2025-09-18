#!/usr/bin/env python3
import os

# Comprehensive 132-directory structure for enterprise Ansible infrastructure
directories = [
    # Root level directories
    "playbooks",
    "roles",
    "inventories",
    "group_vars",
    "host_vars", 
    "docs",
    "tests",
    "scripts",
    "vault",
    "collections",
    "plugins",
    "filters",
    "modules",
    "library",
    "action_plugins",
    "callback_plugins",
    "connection_plugins",
    "lookup_plugins",
    "vars_plugins",
    "strategy_plugins",
    "terminal_plugins",
    "httpapi_plugins",
    "netconf_plugins",
    "cliconf_plugins",
    "become_plugins",
    "cache_plugins",
    "inventory_plugins",
    "shell_plugins",
    "test_plugins",
    "filter_plugins",
    
    # Playbooks structure
    "playbooks/infrastructure",
    "playbooks/applications",
    "playbooks/security",
    "playbooks/monitoring",
    "playbooks/backup",
    "playbooks/deployment",
    "playbooks/maintenance",
    "playbooks/disaster_recovery",
    "playbooks/compliance",
    "playbooks/testing",
    
    # Roles structure - Core standardized roles
    "roles/hx_ca_trust_standardized",
    "roles/hx_ca_trust_standardized/tasks",
    "roles/hx_ca_trust_standardized/handlers",
    "roles/hx_ca_trust_standardized/templates",
    "roles/hx_ca_trust_standardized/files",
    "roles/hx_ca_trust_standardized/vars",
    "roles/hx_ca_trust_standardized/defaults",
    "roles/hx_ca_trust_standardized/meta",
    "roles/hx_ca_trust_standardized/tests",
    
    "roles/hx_domain_join_standardized",
    "roles/hx_domain_join_standardized/tasks",
    "roles/hx_domain_join_standardized/handlers",
    "roles/hx_domain_join_standardized/templates",
    "roles/hx_domain_join_standardized/files",
    "roles/hx_domain_join_standardized/vars",
    "roles/hx_domain_join_standardized/defaults",
    "roles/hx_domain_join_standardized/meta",
    "roles/hx_domain_join_standardized/tests",
    
    "roles/hx_pg_auth_standardized",
    "roles/hx_pg_auth_standardized/tasks",
    "roles/hx_pg_auth_standardized/handlers",
    "roles/hx_pg_auth_standardized/templates",
    "roles/hx_pg_auth_standardized/files",
    "roles/hx_pg_auth_standardized/vars",
    "roles/hx_pg_auth_standardized/defaults",
    "roles/hx_pg_auth_standardized/meta",
    "roles/hx_pg_auth_standardized/tests",
    
    "roles/hx_webui_install_standardized",
    "roles/hx_webui_install_standardized/tasks",
    "roles/hx_webui_install_standardized/handlers",
    "roles/hx_webui_install_standardized/templates",
    "roles/hx_webui_install_standardized/files",
    "roles/hx_webui_install_standardized/vars",
    "roles/hx_webui_install_standardized/defaults",
    "roles/hx_webui_install_standardized/meta",
    "roles/hx_webui_install_standardized/tests",
    
    "roles/hx_litellm_proxy_standardized",
    "roles/hx_litellm_proxy_standardized/tasks",
    "roles/hx_litellm_proxy_standardized/handlers",
    "roles/hx_litellm_proxy_standardized/templates",
    "roles/hx_litellm_proxy_standardized/files",
    "roles/hx_litellm_proxy_standardized/vars",
    "roles/hx_litellm_proxy_standardized/defaults",
    "roles/hx_litellm_proxy_standardized/meta",
    "roles/hx_litellm_proxy_standardized/tests",
    
    # Additional infrastructure roles
    "roles/common",
    "roles/common/tasks",
    "roles/common/handlers", 
    "roles/common/templates",
    "roles/common/files",
    "roles/common/vars",
    "roles/common/defaults",
    "roles/common/meta",
    
    # Inventories structure
    "inventories/production",
    "inventories/staging",
    "inventories/development",
    "inventories/testing",
    "inventories/production/group_vars",
    "inventories/production/host_vars",
    "inventories/staging/group_vars", 
    "inventories/staging/host_vars",
    "inventories/development/group_vars",
    "inventories/development/host_vars",
    "inventories/testing/group_vars",
    "inventories/testing/host_vars",
    
    # Documentation structure
    "docs/architecture",
    "docs/deployment",
    "docs/operations",
    "docs/troubleshooting",
    "docs/security",
    "docs/compliance",
    "docs/diagrams",
    "docs/examples",
    
    # Testing structure
    "tests/unit",
    "tests/integration", 
    "tests/functional",
    "tests/performance",
    "tests/security",
    "tests/molecule",
    "tests/molecule/default",
    "tests/molecule/default/molecule",
    "tests/molecule/default/tests",
    
    # CI/CD structure
    ".github",
    ".github/workflows",
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE",
    
    # Scripts structure
    "scripts/deployment",
    "scripts/maintenance", 
    "scripts/backup",
    "scripts/monitoring",
    "scripts/security",
    "scripts/utilities",
    
    # Vault structure
    "vault/production",
    "vault/staging",
    "vault/development",
    
    # Collections structure
    "collections/ansible_collections",
    "collections/requirements",
]

# Create all directories and add README files
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    readme_path = os.path.join(directory, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write(f"# {directory.replace('/', ' - ').title()}\n\n")
            f.write(f"This directory contains resources for {directory}.\n")

print(f"Created {len(directories)} directories with README files")
