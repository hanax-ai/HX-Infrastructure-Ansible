# Ansible Role: reliability_monitor

Part of the HX Infrastructure Ansible collection.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## Role Variables

Variables prefixed with `reliability_monitor_` can be customized:

```yaml
reliability_monitor_enabled: true
reliability_monitor_config: {}
```

## Dependencies

Listed in `meta/main.yml`.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: reliability_monitor
      reliability_monitor_enabled: true
```

## Testing

```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team - Wave 2 Standardization
