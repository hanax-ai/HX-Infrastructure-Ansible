
# Prompt Templates for HX Infrastructure Documentation

## Overview

This document provides ready-to-use prompt templates for generating and maintaining HX Infrastructure documentation. These templates are based on successful patterns used in the project and include context-specific examples.

## Service Documentation Templates

### Template 1: New Service Documentation
```
Create comprehensive documentation for [SERVICE_NAME] in the HX Infrastructure project.

Context:
- Service type: [Infrastructure/AI-ML/UI/Operations]
- Environment: [Development/Staging/Production]
- Current inventory entry:
```yaml
[paste relevant inventory section]
```

- Related services: [list connected services]
- Current configuration files: [list relevant config files]

Requirements:
1. Service overview and architecture
2. Installation and configuration procedures
3. Deployment and management processes
4. Monitoring and health checks
5. Troubleshooting guide
6. Integration with other HX services
7. Maintenance and backup procedures

Format requirements:
- Use markdown with consistent heading structure (## for main sections, ### for subsections)
- Include code blocks for all configurations and commands
- Add mermaid diagrams for process flows where appropriate
- Include cross-references to related documentation
- Follow HX Infrastructure documentation standards
- Include practical examples using actual hostnames from inventory

Output structure:
# [SERVICE_NAME] Documentation
## Overview
## Architecture
## Installation and Configuration
## Deployment Procedures
## Monitoring and Health Checks
## Troubleshooting
## Integration Points
## Maintenance Procedures
## Related Documentation
```

### Template 2: Service Group Documentation
```
Create documentation for the [SERVICE_GROUP] services in the HX Infrastructure project.

Context:
- Service group: [Infrastructure/AI-ML/UI/Operations]
- Services included: [list all services in group]
- Current inventory structure:
```yaml
[paste relevant group structure from inventory]
```

- Environment: [specify environment or "all environments"]
- Integration points: [list how this group integrates with others]

Requirements:
1. Service group overview and relationships
2. Shared configuration and dependencies
3. Group deployment procedures
4. Inter-service communication patterns
5. Group monitoring and alerting
6. Troubleshooting service interactions
7. Scaling and capacity planning
8. Disaster recovery procedures

Format requirements:
- Use markdown with clear service separation
- Include architecture diagrams showing service relationships
- Provide group-level and individual service configurations
- Include practical deployment examples
- Cross-reference individual service documentation
- Follow HX Infrastructure documentation standards

Output structure:
# [SERVICE_GROUP] Services Documentation
## Group Overview
## Service Relationships
## Shared Configuration
## Deployment Procedures
## Inter-Service Communication
## Monitoring and Alerting
## Troubleshooting
## Scaling and Capacity Planning
## Disaster Recovery
## Individual Service References
```

## Process Documentation Templates

### Template 3: Operational Process Documentation
```
Create process documentation for [PROCESS_NAME] in the HX Infrastructure project.

Context:
- Process type: [Deployment/Maintenance/Troubleshooting/Discovery]
- Stakeholders involved: [list roles and responsibilities]
- Current workflow: [describe existing process if any]
- Integration points: [list related processes and systems]
- Frequency: [how often this process is executed]

Requirements:
1. Process overview and objectives
2. Prerequisites and preparation steps
3. Step-by-step procedure with decision points
4. Role assignments and responsibilities
5. Tools and resources required
6. Quality checkpoints and validation
7. Escalation procedures
8. Documentation and reporting requirements

Format requirements:
- Use numbered steps for procedures
- Include decision flowcharts using mermaid
- Provide checklists for complex procedures
- Include example commands and configurations
- Add troubleshooting sections for common issues
- Cross-reference related processes and documentation

Output structure:
# [PROCESS_NAME] Process Documentation
## Overview and Objectives
## Prerequisites
## Procedure Steps
## Roles and Responsibilities
## Tools and Resources
## Quality Checkpoints
## Escalation Procedures
## Documentation Requirements
## Related Processes
```

### Template 4: Troubleshooting Guide
```
Create a troubleshooting guide for [SYSTEM/SERVICE] in the HX Infrastructure project.

Context:
- System/Service: [specific system or service name]
- Common issues: [list known issues if any]
- Monitoring tools available: [list monitoring and logging tools]
- Service dependencies: [list dependent services]
- Current inventory configuration:
```yaml
[paste relevant inventory section]
```

Requirements:
1. Common symptoms and their causes
2. Diagnostic procedures and tools
3. Step-by-step resolution procedures
4. Prevention strategies
5. Escalation criteria and procedures
6. Recovery and rollback procedures
7. Post-incident documentation requirements

Format requirements:
- Organize by symptom categories
- Include diagnostic commands and expected outputs
- Provide decision trees for complex troubleshooting
- Include log file locations and analysis tips
- Add prevention and monitoring recommendations
- Cross-reference related troubleshooting guides

Output structure:
# [SYSTEM/SERVICE] Troubleshooting Guide
## Common Issues Overview
## Diagnostic Tools and Procedures
## Issue Categories
### [Category 1]
#### Symptoms
#### Diagnosis
#### Resolution
#### Prevention
### [Category 2]
[repeat structure]
## Escalation Procedures
## Recovery and Rollback
## Post-Incident Actions
```

## Configuration Documentation Templates

### Template 5: Configuration Management Documentation
```
Create configuration documentation for [CONFIGURATION_AREA] in the HX Infrastructure project.

Context:
- Configuration area: [Ansible/Inventory/Service-specific/Environment]
- Current configuration files:
```
[paste relevant configuration content]
```

- Environment variations: [describe differences between dev/staging/prod]
- Dependencies: [list configuration dependencies]
- Integration requirements: [list systems that depend on this configuration]

Requirements:
1. Configuration overview and purpose
2. File structure and organization
3. Configuration options and their effects
4. Environment-specific variations
5. Validation and testing procedures
6. Deployment and update procedures
7. Backup and recovery procedures
8. Troubleshooting configuration issues

Format requirements:
- Include complete configuration examples
- Provide comparison tables for environment differences
- Add validation commands and expected results
- Include migration procedures for configuration changes
- Cross-reference related configuration documentation

Output structure:
# [CONFIGURATION_AREA] Configuration Documentation
## Overview and Purpose
## File Structure
## Configuration Options
## Environment Variations
## Validation Procedures
## Deployment Procedures
## Backup and Recovery
## Troubleshooting
## Related Configurations
```

## Update and Maintenance Templates

### Template 6: Documentation Update
```
Update the existing [DOCUMENT_NAME] documentation to address [SPECIFIC_CHANGES].

Context:
- Current document location: [file path]
- Changes required: [describe specific changes needed]
- Reason for update: [bug fix/new feature/process change/feedback]
- Related changes: [list other documents that may need updates]

Current document content:
```markdown
[paste relevant sections of current document]
```

Requirements:
1. Maintain consistency with existing document structure
2. Update all affected sections
3. Ensure cross-references remain accurate
4. Update examples and code blocks as needed
5. Maintain compatibility with related documentation
6. Follow HX Infrastructure documentation standards

Format requirements:
- Preserve existing heading structure unless restructuring is needed
- Update table of contents if structure changes
- Maintain consistent formatting with rest of document
- Update modification date and version information
- Ensure all links and references are still valid

Instructions:
- Identify all sections that need updates
- Provide the complete updated sections
- Highlight what has changed and why
- Ensure consistency with related documentation
- Validate that examples and procedures still work
```

### Template 7: Cross-Reference Update
```
Update cross-references and links in HX Infrastructure documentation following [CHANGE_DESCRIPTION].

Context:
- Change made: [describe the change that affects references]
- Documents affected: [list documents that need reference updates]
- New structure/location: [describe new organization if applicable]

Requirements:
1. Identify all documents with references to changed content
2. Update internal links and cross-references
3. Update table of contents and navigation
4. Ensure consistency across all documentation
5. Validate that all links work correctly

Format requirements:
- Maintain existing link formats and styles
- Use relative paths for internal documentation links
- Ensure link text is descriptive and accurate
- Update any navigation menus or indexes

Instructions:
- Scan all documentation for references to changed content
- Provide updated link syntax for each affected reference
- Ensure bidirectional references are maintained
- Test that all updated links work correctly
```

## Quality Assurance Templates

### Template 8: Documentation Review
```
Perform a comprehensive review of [DOCUMENT_NAME] for quality, accuracy, and completeness.

Context:
- Document location: [file path]
- Document purpose: [describe what the document is meant to accomplish]
- Target audience: [describe intended users]
- Last review date: [if known]

Review criteria:
1. Technical accuracy of all information
2. Completeness of required sections
3. Clarity and readability
4. Consistency with documentation standards
5. Currency of information and examples
6. Effectiveness of cross-references
7. Usability for intended audience

Current document:
```markdown
[paste document content]
```

Requirements:
1. Identify any technical inaccuracies
2. Note missing or incomplete sections
3. Suggest improvements for clarity
4. Check compliance with documentation standards
5. Verify that examples and procedures work
6. Recommend updates for outdated information
7. Assess overall document effectiveness

Output format:
- Provide specific feedback for each section
- Suggest concrete improvements
- Identify priority levels for different issues
- Recommend next review date
- Provide overall quality assessment
```

## Usage Guidelines

### Selecting the Right Template
1. **New Service**: Use Template 1 for individual services, Template 2 for service groups
2. **Process Documentation**: Use Template 3 for operational processes, Template 4 for troubleshooting
3. **Configuration**: Use Template 5 for configuration documentation
4. **Updates**: Use Template 6 for content updates, Template 7 for structural changes
5. **Quality**: Use Template 8 for comprehensive reviews

### Customizing Templates
1. Replace all bracketed placeholders with specific information
2. Paste relevant configuration or inventory content where indicated
3. Adjust requirements based on specific documentation needs
4. Modify output structure if different organization is needed

### Best Practices
1. Always provide complete context information
2. Include actual configuration examples from the project
3. Specify format requirements clearly
4. Request specific output structure
5. Ask for cross-references to related documentation
6. Include validation and testing procedures

## Related Documentation

- [Generative Prompt Guide](../generative_prompt_guide.md)
- [Documentation Standards](../standards/Documentation_Standards.md)
- [Process for New Discoveries](../process/new_discoveries.md)
