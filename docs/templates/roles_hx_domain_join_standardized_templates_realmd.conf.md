# Template: roles/hx_domain_join_standardized/templates/realmd.conf.j2

**Path:** `./roles/hx_domain_join_standardized/templates/realmd.conf.j2`  
**Size:** 915 bytes (40 lines)  
**Last Modified:** 2025-09-17T13:11:56.776000

## Description

*No documentation comments found in template.*

### Variables

| Variable | Type | Description |
|----------|------|-------------|
| `ansible_distribution` | *unknown* | *Add description* |
| `ansible_distribution_version` | *unknown* | *Add description* |
| `ansible_hostname` | *unknown* | *Add description* |
| `ansible_managed` | *unknown* | *Add description* |
| `hx_ad_computer_name` | *unknown* | *Add description* |
| `hx_ad_domain_controller` | *unknown* | *Add description* |
| `hx_ad_domain_lower` | *unknown* | *Add description* |
| `hx_ad_ou_path` | *unknown* | *Add description* |
| `hx_ad_realm_upper` | *unknown* | *Add description* |
| `hx_domain_require_encryption` | *unknown* | *Add description* |
| `hx_domain_verify_certificates` | *unknown* | *Add description* |
| `hx_home_dir_base` | *unknown* | *Add description* |
| `hx_login_shell` | *unknown* | *Add description* |

### Filters Used

- `upper`

### Logic Structures

**Conditionals:**
- `hx_ad_domain_controller`
- `hx_ad_computer_name != ansible_hostname | upper`
- `hx_ad_ou_path`
- `hx_domain_require_encryption`
- `hx_domain_verify_certificates`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/hx_domain_join_standardized/templates/realmd.conf.j2
    dest: /path/to/destination
  vars:
    ansible_distribution: "{ ansible_distribution }"
    ansible_managed: "{ ansible_managed }"
    hx_ad_domain_lower: "{ hx_ad_domain_lower }"
    hx_domain_verify_certificates: "{ hx_domain_verify_certificates }"
    hx_login_shell: "{ hx_login_shell }"
```

### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates


---
*Generated automatically by Template Documentation Generator*
