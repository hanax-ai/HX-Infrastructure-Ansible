#!/bin/bash
# Role Interface Normalization Script
# Part of Wave 2 - HX-Approval-Plan Action #3

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ROLES_DIR="$REPO_ROOT/roles"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

# Function to create README stub for a role
create_role_readme() {
    local role_name="$1"
    local readme_path="$ROLES_DIR/$role_name/README.md"
    
    if [[ -f "$readme_path" ]]; then
        log "README exists for $role_name, checking if it needs normalization..."
        # Check if it has the standard sections
        if ! grep -q "## Requirements" "$readme_path" || ! grep -q "## Role Variables" "$readme_path"; then
            warn "README for $role_name missing standard sections, updating..."
        else
            log "README for $role_name appears complete"
            return 0
        fi
    fi
    
    log "Creating/updating README for role: $role_name"
    cat > "$readme_path" <<EOF
# Ansible Role: $role_name

[![CI](https://i.ytimg.com/vi/HiQDsFPf0s4/maxresdefault.jpg)

This role is part of the HX Infrastructure Ansible collection.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## Role Variables

Available variables are listed below, along with default values (see \`defaults/main.yml\`):

### Required Variables

None by default.

### Optional Variables (Tunables)

Variables prefixed with \`${role_name}_\` can be customized:

\`\`\`yaml
# Example configurable variables
${role_name}_enabled: true
${role_name}_config: {}
\`\`\`

### Internal Variables

Variables in \`vars/main.yml\` are internal invariants and should not be overridden.

## Dependencies

Listed in \`meta/main.yml\`.

## Example Playbook

\`\`\`yaml
- hosts: servers
  roles:
    - role: $role_name
      ${role_name}_enabled: true
\`\`\`

## Testing

This role includes Molecule tests. Run them with:

\`\`\`bash
molecule test
\`\`\`

## License

MIT / BSD

## Author Information

HX Infrastructure Team

## Change Log

- Initial role creation and standardization per HX-Approval-Plan Wave 2
EOF
    success "README created/updated for $role_name"
}

# Function to ensure proper directory structure
ensure_role_structure() {
    local role_name="$1"
    local role_path="$ROLES_DIR/$role_name"
    
    log "Ensuring proper structure for role: $role_name"
    
    # Core directories
    mkdir -p "$role_path/defaults"
    mkdir -p "$role_path/vars"
    mkdir -p "$role_path/tasks"
    mkdir -p "$role_path/handlers"
    mkdir -p "$role_path/meta"
    mkdir -p "$role_path/molecule/default"
    
    # Ensure main.yml files exist
    for dir in defaults vars tasks handlers meta; do
        local main_file="$role_path/$dir/main.yml"
        if [[ ! -f "$main_file" ]]; then
            case "$dir" in
                "defaults")
                    cat > "$main_file" <<EOF
---
# Default variables for $role_name role
# These are tunables that can be overridden

# Enable/disable role functionality
${role_name}_enabled: true

# Role-specific configuration
${role_name}_config: {}
EOF
                    ;;
                "vars")
                    cat > "$main_file" <<EOF
---
# Internal variables for $role_name role
# These are invariants and should NOT be overridden

# Role metadata
${role_name}_role_version: "1.0.0"
${role_name}_role_name: "$role_name"
EOF
                    ;;
                "tasks")
                    if [[ ! -f "$main_file" ]]; then
                        cat > "$main_file" <<EOF
---
# Main tasks for $role_name role

- name: "Verify role prerequisites"
  ansible.builtin.assert:
    that:
      - ${role_name}_enabled is defined
      - ${role_name}_enabled is boolean
    fail_msg: "Role $role_name requires ${role_name}_enabled to be defined as boolean"
    success_msg: "Role $role_name prerequisites verified"

- name: "Display role information"
  ansible.builtin.debug:
    msg: "Executing role {{ ${role_name}_role_name }} version {{ ${role_name}_role_version }}"
  when: ${role_name}_enabled | bool

# TODO: Implement actual role tasks
- name: "Placeholder for $role_name implementation"
  ansible.builtin.debug:
    msg: "Role $role_name is enabled and ready for implementation"
  when: ${role_name}_enabled | bool
EOF
                    fi
                    ;;
                "handlers")
                    cat > "$main_file" <<EOF
---
# Handlers for $role_name role

# Example handler - customize as needed
- name: "restart $role_name service"
  ansible.builtin.service:
    name: "{{ ${role_name}_service_name | default('example-service') }}"
    state: restarted
  when: ${role_name}_enabled | bool
EOF
                    ;;
                "meta")
                    cat > "$main_file" <<EOF
---
galaxy_info:
  role_name: $role_name
  namespace: hx_infrastructure
  author: HX Infrastructure Team
  description: HX Infrastructure role for $role_name
  company: HX Infrastructure
  license: MIT
  min_ansible_version: "2.9"
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: CentOS
      versions:
        - "8"
        - "9"
    - name: RedHat
      versions:
        - "8"
        - "9"
  galaxy_tags:
    - infrastructure
    - automation
    - hx

dependencies: []
EOF
                    ;;
            esac
            success "Created $main_file"
        fi
    done
}

# Function to create basic Molecule scaffold
create_molecule_scaffold() {
    local role_name="$1"
    local molecule_path="$ROLES_DIR/$role_name/molecule/default"
    
    log "Creating Molecule scaffold for role: $role_name"
    
    # molecule.yml
    cat > "$molecule_path/molecule.yml" <<EOF
---
role_name_check_mode: false
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: quay.io/ansible/molecule-ubuntu:latest
    pre_build_image: true
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
provisioner:
  name: ansible
  config_options:
    defaults:
      interpreter_python: auto_silent
      callback_whitelist: profile_tasks, timer, yaml
    ssh_connection:
      pipelining: false
verifier:
  name: ansible
EOF
    
    # converge.yml
    cat > "$molecule_path/converge.yml" <<EOF
---
- name: Converge
  hosts: all
  become: true
  
  vars:
    ${role_name}_enabled: true
    
  roles:
    - role: $role_name
EOF
    
    # verify.yml
    cat > "$molecule_path/verify.yml" <<EOF
---
- name: Verify
  hosts: all
  gather_facts: false
  tasks:
    - name: "Verify $role_name role execution"
      ansible.builtin.debug:
        msg: "Role $role_name verification placeholder"
        
    # TODO: Add specific verification tasks
EOF
    
    success "Molecule scaffold created for $role_name"
}

# Function to normalize a single role
normalize_role() {
    local role_name="$1"
    
    log "=== Normalizing role: $role_name ==="
    
    # Skip geerlingguy roles for now (external collection)
    if [[ "$role_name" =~ ^geerlingguy\. ]]; then
        log "Skipping external role: $role_name"
        return 0
    fi
    
    ensure_role_structure "$role_name"
    create_role_readme "$role_name"
    create_molecule_scaffold "$role_name"
    
    success "Role normalization complete: $role_name"
    echo
}

# Main execution
main() {
    log "Starting Role Interface Normalization - Wave 2"
    log "Working directory: $REPO_ROOT"
    
    if [[ ! -d "$ROLES_DIR" ]]; then
        error "Roles directory not found: $ROLES_DIR"
        exit 1
    fi
    
    # Get all role directories
    local roles=()
    while IFS= read -r -d '' role_dir; do
        role_name=$(basename "$role_dir")
        roles+=("$role_name")
    done < <(find "$ROLES_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
    
    log "Found ${#roles[@]} roles to normalize"
    
    # Process each role
    local count=0
    for role in "${roles[@]}"; do
        ((count++))
        log "Processing role $count/${#roles[@]}: $role"
        normalize_role "$role"
    done
    
    success "Role Interface Normalization Complete!"
    success "Processed ${#roles[@]} roles"
    
    log "Next steps:"
    log "1. Review the changes"
    log "2. Test with: find roles/ -name 'molecule.yml' | wc -l"
    log "3. Run lint checks"
    log "4. Commit changes"
}

# Execute main function
main "$@"