---
# Wave 3 — Module Migration & Idempotency Plan

I have read and understood RULES.md before beginning this task.

## Objective

Replace obvious shell/command module usage with appropriate Ansible modules and add idempotency controls (creates/removes/changed_when) to ensure --check mode safety across all roles.

## Scope

- **Target**: All 56+ roles in the repository
- **Focus**: Shell/command tasks that can be replaced with native Ansible modules
- **Safety**: Ensure all tasks are idempotent and --check mode compatible
- **Quality**: Maintain existing functionality while improving automation standards

## Implementation Strategy

### Phase 1: Discovery & Assessment
- Scan all roles for shell/command module usage
- Identify obvious candidates for module replacement (package installs, file operations, service management)
- Document current idempotency gaps

### Phase 2: Module Migration
- Replace shell/command with appropriate modules:
  - `shell: apt install` → `ansible.builtin.package`
  - `command: systemctl` → `ansible.builtin.systemd`
  - `shell: mkdir` → `ansible.builtin.file`
  - `command: curl/wget` → `ansible.builtin.get_url`
  - File manipulation → `ansible.builtin.lineinfile`, `ansible.builtin.replace`

### Phase 3: Idempotency Controls
- Add `creates:` parameter where appropriate
- Add `removes:` parameter for cleanup tasks
- Add `changed_when:` conditions for tasks that don't naturally report changes
- Ensure `--check` mode compatibility

## Success Criteria

- [ ] All obvious shell/command usage replaced with native modules
- [ ] All tasks have appropriate idempotency controls
- [ ] `ansible-playbook --check` runs successfully on all playbooks
- [ ] No functional behavior changes
- [ ] CI passes with improved lint scores

## Risk Mitigation

- Test changes in development environment first
- Maintain backward compatibility
- Document any breaking changes
- Preserve existing error handling patterns

---

**Status**: Planning Phase  
**Next Steps**: Begin discovery scan of roles for shell/command usage
