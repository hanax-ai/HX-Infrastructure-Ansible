# Template: templates/phase3_validation_report.json.j2

**Path:** `./templates/phase3_validation_report.json.j2`  
**Size:** 3284 bytes (65 lines)  
**Last Modified:** 2025-09-18T07:03:16.143000

## Description

*No documentation comments found in template.*

### Filters Used

- `default`
- `length`
- `round`
- `to_json`

### Logic Structures

**Conditionals:**
- `naming_compliance_report is defined and naming_compliance_report.non_compliant_variables | length > 0`

### Usage Example

```yaml
- name: Apply template
  template:
    src: templates/phase3_validation_report.json.j2
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
