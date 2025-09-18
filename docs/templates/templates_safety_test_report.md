# Template: templates/safety_test_report.j2

**Path:** `./templates/safety_test_report.j2`  
**Size:** 1478 bytes (56 lines)  
**Last Modified:** 2025-09-18T06:50:50.938000

## Description

*No documentation comments found in template.*

### Variables

| Variable | Type | Description |
|----------|------|-------------|
| `ansible_hostname` | *unknown* | *Add description* |
| `ansible_user_id` | *unknown* | *Add description* |
| `ansible_version` | *unknown* | *Add description* |
| `test_results` | *unknown* | *Add description* |
| `test_timestamp` | *unknown* | *Add description* |

### Usage Example

```yaml
- name: Apply template
  template:
    src: templates/safety_test_report.j2
    dest: /path/to/destination
  vars:
    ansible_hostname: "{ ansible_hostname }"
    ansible_user_id: "{ ansible_user_id }"
    ansible_version: "{ ansible_version }"
    test_results: "{ test_results }"
    test_timestamp: "{ test_timestamp }"
```

### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates


---
*Generated automatically by Template Documentation Generator*
