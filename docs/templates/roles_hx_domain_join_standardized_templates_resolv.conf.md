# Template: roles/hx_domain_join_standardized/templates/resolv.conf.j2

**Path:** `./roles/hx_domain_join_standardized/templates/resolv.conf.j2`  
**Size:** 308 bytes (16 lines)  
**Last Modified:** 2025-09-17T13:11:56.806000

## Description

*No documentation comments found in template.*

### Variables

| Variable | Type | Description |
|----------|------|-------------|
| `ansible_managed` | *unknown* | *Add description* |
| `hx_dns_nameservers` | *unknown* | *Add description* |
| `hx_dns_search_domains` | *unknown* | *Add description* |

### Logic Structures

**Loops:**
- `nameserver in hx_dns_nameservers`
- `domain in hx_dns_search_domains`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/hx_domain_join_standardized/templates/resolv.conf.j2
    dest: /path/to/destination
  vars:
    ansible_managed: "{ ansible_managed }"
    hx_dns_nameservers: "{ hx_dns_nameservers }"
    hx_dns_search_domains: "{ hx_dns_search_domains }"
```

### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates


---
*Generated automatically by Template Documentation Generator*
