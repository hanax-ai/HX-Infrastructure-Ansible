# Ansible Role: performance_optimization

Part of the HX Infrastructure Ansible collection.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## Role Variables

Variables prefixed with `performance_optimization_` can be customized:

```yaml
performance_optimization_enabled: true
performance_optimization_config: {}
```

## Dependencies

Listed in `meta/main.yml`.

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: performance_optimization
      performance_optimization_enabled: true
```

## Testing

```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team - Wave 2 Standardization
