# Template: roles/hx_domain_join_standardized/templates/security_audit.j2

**Path:** `./roles/hx_domain_join_standardized/templates/security_audit.j2`  
**Size:** 3320 bytes (96 lines)  
**Last Modified:** 2025-09-17T13:11:56.799000

## Description

*No documentation comments found in template.*

### Filters Used

- `default`
- `join`
- `ternary`

### Logic Structures

**Conditionals:**
- `hx_domain_require_encryption`
- `hx_sudo_enabled`
- `hx_ldaps_cert_check is defined`
- `hx_ldaps_cert_check.rc != 0`
- `hx_weak_auth_check is defined`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/hx_domain_join_standardized/templates/security_audit.j2
    dest: /path/to/destination
  vars:
```

### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates


---
*Generated automatically by Template Documentation Generator*
