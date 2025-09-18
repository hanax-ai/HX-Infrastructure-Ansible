# Template: roles/ssh_key_management/templates/rotate_ssh_keys.sh.j2

**Path:** `./roles/ssh_key_management/templates/rotate_ssh_keys.sh.j2`  
**Size:** 4468 bytes (142 lines)  
**Last Modified:** 2025-09-18T06:48:19.706000

## Description

*No documentation comments found in template.*

### Variables

| Variable | Type | Description |
|----------|------|-------------|
| `ansible_date_time` | *unknown* | *Add description* |
| `ansible_playbook_path` | *unknown* | *Add description* |
| `ansible_user` | *unknown* | *Add description* |
| `inventory_file` | *unknown* | *Add description* |
| `inventory_hostname` | *unknown* | *Add description* |
| `ssh_key_backup_dir` | *unknown* | *Add description* |
| `ssh_key_log_dir` | *unknown* | *Add description* |
| `ssh_key_private_path` | *unknown* | *Add description* |
| `ssh_key_rotation_days` | *unknown* | *Add description* |
| `ssh_key_rotation_warning_days` | *unknown* | *Add description* |
| `ssh_key_type` | *unknown* | *Add description* |
| `ssh_rotation_notification_email` | *unknown* | *Add description* |

### Filters Used

- `awk`
- `default`
- `error_exit`
- `sort`
- `tail`
- `tee`
- `true`
- `xargs`

### Logic Structures

**Conditionals:**
- `ssh_rotation_notification_email is defined`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/ssh_key_management/templates/rotate_ssh_keys.sh.j2
    dest: /path/to/destination
  vars:
    ansible_date_time: "{ ansible_date_time }"
    ssh_key_private_path: "{ ssh_key_private_path }"
    ssh_key_rotation_warning_days: "{ ssh_key_rotation_warning_days }"
    ssh_key_type: "{ ssh_key_type }"
    ssh_rotation_notification_email: "{ ssh_rotation_notification_email }"
```

### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates


---
*Generated automatically by Template Documentation Generator*
