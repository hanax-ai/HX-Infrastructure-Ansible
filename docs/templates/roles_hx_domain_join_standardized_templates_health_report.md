# Template: roles/hx_domain_join_standardized/templates/health_report.j2

**Path:** `./roles/hx_domain_join_standardized/templates/health_report.j2`  
**Size:** 4600 bytes (127 lines)  
**Last Modified:** 2025-09-17T13:11:56.816000

## Description

*No documentation comments found in template.*

### Variables

| Variable | Type | Description |
|----------|------|-------------|
| `ansible_architecture` | *unknown* | *Add description* |
| `ansible_date_time` | *unknown* | *Add description* |
| `ansible_distribution` | *unknown* | *Add description* |
| `ansible_distribution_version` | *unknown* | *Add description* |
| `ansible_fqdn` | *unknown* | *Add description* |
| `ansible_hostname` | *unknown* | *Add description* |
| `ansible_managed` | *unknown* | *Add description* |
| `hx_ad_computer_fqdn` | *unknown* | *Add description* |
| `hx_ad_computer_name` | *unknown* | *Add description* |
| `hx_ad_domain` | *unknown* | *Add description* |
| `hx_ad_realm` | *unknown* | *Add description* |
| `hx_dc_connectivity_test` | *unknown* | *Add description* |
| `hx_dns_resolution_test` | *unknown* | *Add description* |
| `hx_domain_join_version` | *unknown* | *Add description* |
| `hx_domain_log_dir` | *unknown* | *Add description* |
| `hx_domain_membership_check` | *unknown* | *Add description* |
| `hx_group_lookup_test` | *unknown* | *Add description* |
| `hx_health_checks_passed` | *unknown* | *Add description* |
| `hx_health_checks_total` | *unknown* | *Add description* |
| `hx_home_dir_test` | *unknown* | *Add description* |
| `hx_kerberos_ticket_test` | *unknown* | *Add description* |
| `hx_krb5_conf_path` | *unknown* | *Add description* |
| `hx_nsswitch_conf_path` | *unknown* | *Add description* |
| `hx_realmd_conf_path` | *unknown* | *Add description* |
| `hx_sssd_cache_check` | *unknown* | *Add description* |
| `hx_sssd_conf_path` | *unknown* | *Add description* |
| `hx_sssd_service_status` | *unknown* | *Add description* |
| `hx_user_lookup_test` | *unknown* | *Add description* |

### Filters Used

- `default`
- `int`
- `round`
- `ternary`

### Logic Structures

**Conditionals:**
- `hx_domain_membership_check is defined`
- `hx_domain_membership_check.rc == 0`
- `hx_sssd_service_status is defined`
- `hx_dns_resolution_test is defined`
- `hx_dns_resolution_test.rc != 0`

### Usage Example

```yaml
- name: Apply template
  template:
    src: roles/hx_domain_join_standardized/templates/health_report.j2
    dest: /path/to/destination
  vars:
    ansible_architecture: "{ ansible_architecture }"
    ansible_distribution: "{ ansible_distribution }"
    hx_ad_domain: "{ hx_ad_domain }"
    hx_domain_join_version: "{ hx_domain_join_version }"
    hx_user_lookup_test: "{ hx_user_lookup_test }"
```

### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates


---
*Generated automatically by Template Documentation Generator*
