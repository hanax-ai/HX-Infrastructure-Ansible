# Ansible Role: disaster_recovery

Part of the HX Infrastructure Ansible collection.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## Role Variables

Variables prefixed with `disaster_recovery_` can be customized:

```yaml
disaster_recovery_enabled: true
disaster_recovery_config: {}
```

## Dependencies

Listed in `meta/main.yml`.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: disaster_recovery
      disaster_recovery_enabled: true
```

## Testing

```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team - Wave 2 Standardization
