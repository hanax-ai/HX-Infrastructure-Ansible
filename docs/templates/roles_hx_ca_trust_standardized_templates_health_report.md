# Template: roles/hx_ca_trust_standardized/templates/health_report.j2

**Path:** `./roles/hx_ca_trust_standardized/templates/health_report.j2`  
**Size:** 3477 bytes (101 lines)  
**Last Modified:** 2025-09-17T13:04:18.384000

## Description

*No documentation comments found in template.*

### Filters Used

- `default`
- `int`
- `round`
- `strftime`
- `ternary`

### Logic Structures

**Conditionals:**
- `hx_ca_parse_test is defined`
- `hx_ca_parse_test.rc == 0`
- `hx_ca_trust_store_check is defined`
- `hx_ca_trust_store_check.rc != 0`
- `hx_ca_ssl_test is defined`

**Loops:**
- `result in hx_ca_target_validation.results`
- `result in hx_ca_health_endpoint_check.results`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/hx_ca_trust_standardized/templates/health_report.j2
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
