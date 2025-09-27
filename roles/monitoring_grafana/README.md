# Ansible Role: monitoring_grafana

Part of the HX Infrastructure Ansible collection.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## Role Variables

Variables prefixed with `monitoring_grafana_` can be customized:

```yaml
monitoring_grafana_enabled: true
monitoring_grafana_config: {}
```

## Dependencies

Listed in `meta/main.yml`.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: monitoring_grafana
      monitoring_grafana_enabled: true
```

## Testing

```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team - Wave 2 Standardization
