# Template: roles/hx_ca_trust_standardized/templates/security_audit.j2

**Path:** `./roles/hx_ca_trust_standardized/templates/security_audit.j2`  
**Size:** 2641 bytes (82 lines)  
**Last Modified:** 2025-09-17T13:04:18.377000

## Description

*No documentation comments found in template.*

### Filters Used

- `default`
- `length`
- `ternary`

### Logic Structures

**Conditionals:**
- `hx_ca_actual_fingerprint is defined`
- `hx_ca_cert_info is defined`
- `hx_ca_chain_verify is defined`
- `hx_ca_chain_verify.rc != 0`
- `hx_ca_expiry_check is defined`

**Loops:**
- `target in hx_ca_san_check_targets`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/hx_ca_trust_standardized/templates/security_audit.j2
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
