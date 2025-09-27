# Ansible Role: enterprise_integration

Part of the HX Infrastructure Ansible collection.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## Role Variables

Variables prefixed with `enterprise_integration_` can be customized:

```yaml
enterprise_integration_enabled: true
enterprise_integration_config: {}
```

## Dependencies

Listed in `meta/main.yml`.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: enterprise_integration
      enterprise_integration_enabled: true
```

## Testing

```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team - Wave 2 Standardization
