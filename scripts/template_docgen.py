
#!/usr/bin/env python3
"""
Template Documentation Generator
Automatically generates comprehensive documentation for Jinja2 templates
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader, meta
from datetime import datetime

class TemplateDocGenerator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.env = Environment(loader=FileSystemLoader(str(self.base_path)))
        
    def extract_template_info(self, template_path: str) -> Dict[str, Any]:
        """Extract comprehensive information from template"""
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        template_name = os.path.relpath(template_path, self.base_path)
        
        # Parse template
        try:
            ast = self.env.parse(content, name=template_name)
            variables = list(meta.find_undeclared_variables(ast))
        except Exception:
            variables = []
        
        # Extract documentation comments
        doc_comments = re.findall(r'{#\s*(.*?)\s*#}', content, re.DOTALL)
        
        # Extract blocks
        blocks = re.findall(r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock', content, re.DOTALL)
        
        # Extract macros
        macros = re.findall(r'{%\s*macro\s+(\w+)\s*\((.*?)\)\s*%}(.*?){%\s*endmacro', content, re.DOTALL)
        
        # Extract includes/extends
        includes = re.findall(r'{%\s*include\s+["\']([^"\']+)["\']', content)
        extends = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']', content)
        
        # Extract filters used
        filters = list(set(re.findall(r'\|\s*(\w+)', content)))
        
        # Extract conditionals and loops
        conditionals = re.findall(r'{%\s*if\s+(.*?)\s*%}', content)
        loops = re.findall(r'{%\s*for\s+(.*?)\s*%}', content)
        
        return {
            "name": template_name,
            "path": template_path,
            "size": len(content),
            "lines": len(content.splitlines()),
            "variables": variables,
            "blocks": [{"name": name, "content": content.strip()} for name, content in blocks],
            "macros": [{"name": name, "params": params.strip(), "content": content.strip()} 
                      for name, params, content in macros],
            "includes": includes,
            "extends": extends.group(1) if extends else None,
            "filters": filters,
            "conditionals": conditionals,
            "loops": loops,
            "documentation": doc_comments,
            "last_modified": datetime.fromtimestamp(os.path.getmtime(template_path)).isoformat()
        }
    
    def generate_markdown_doc(self, template_info: Dict[str, Any]) -> str:
        """Generate markdown documentation for a template"""
        doc = f"""# Template: {template_info['name']}

**Path:** `{template_info['path']}`  
**Size:** {template_info['size']} bytes ({template_info['lines']} lines)  
**Last Modified:** {template_info['last_modified']}

## Description

"""
        
        # Add existing documentation
        if template_info['documentation']:
            doc += "### Existing Documentation\n\n"
            for comment in template_info['documentation']:
                doc += f"```\n{comment.strip()}\n```\n\n"
        else:
            doc += "*No documentation comments found in template.*\n\n"
        
        # Template inheritance
        if template_info['extends']:
            doc += f"### Inheritance\n\nThis template extends: `{template_info['extends']}`\n\n"
        
        if template_info['includes']:
            doc += "### Includes\n\n"
            for include in template_info['includes']:
                doc += f"- `{include}`\n"
            doc += "\n"
        
        # Variables
        if template_info['variables']:
            doc += "### Variables\n\n"
            doc += "| Variable | Type | Description |\n"
            doc += "|----------|------|-------------|\n"
            for var in sorted(template_info['variables']):
                doc += f"| `{var}` | *unknown* | *Add description* |\n"
            doc += "\n"
        
        # Blocks
        if template_info['blocks']:
            doc += "### Blocks\n\n"
            for block in template_info['blocks']:
                doc += f"#### Block: `{block['name']}`\n\n"
                doc += "```jinja2\n"
                doc += block['content'][:200] + ("..." if len(block['content']) > 200 else "")
                doc += "\n```\n\n"
        
        # Macros
        if template_info['macros']:
            doc += "### Macros\n\n"
            for macro in template_info['macros']:
                doc += f"#### Macro: `{macro['name']}({macro['params']})`\n\n"
                doc += "```jinja2\n"
                doc += macro['content'][:200] + ("..." if len(macro['content']) > 200 else "")
                doc += "\n```\n\n"
        
        # Filters
        if template_info['filters']:
            doc += "### Filters Used\n\n"
            for filter_name in sorted(template_info['filters']):
                doc += f"- `{filter_name}`\n"
            doc += "\n"
        
        # Logic structures
        if template_info['conditionals'] or template_info['loops']:
            doc += "### Logic Structures\n\n"
            
            if template_info['conditionals']:
                doc += "**Conditionals:**\n"
                for cond in template_info['conditionals'][:5]:  # Limit to first 5
                    doc += f"- `{cond.strip()}`\n"
                doc += "\n"
            
            if template_info['loops']:
                doc += "**Loops:**\n"
                for loop in template_info['loops'][:5]:  # Limit to first 5
                    doc += f"- `{loop.strip()}`\n"
                doc += "\n"
        
        # Usage examples
        doc += """### Usage Example

```yaml
- name: Apply template
  template:
    src: """ + template_info['name'] + """
    dest: /path/to/destination
  vars:
"""
        
        for var in sorted(template_info['variables'][:5]):  # Show first 5 variables
            doc += f"    {var}: \"{{ {var} }}\"\n"
        
        doc += "```\n\n"
        
        # Best practices
        doc += """### Best Practices

- Ensure all variables are defined in defaults or passed explicitly
- Use appropriate filters for data sanitization
- Add comments for complex logic
- Test template with various input scenarios

### Related Templates

"""
        
        if template_info['extends']:
            doc += f"- **Parent:** `{template_info['extends']}`\n"
        
        for include in template_info['includes']:
            doc += f"- **Includes:** `{include}`\n"
        
        doc += "\n---\n*Generated automatically by Template Documentation Generator*\n"
        
        return doc
    
    def generate_docs_for_templates(self, template_list: List[str], output_dir: str = "docs/templates"):
        """Generate documentation for all templates"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate index
        index_content = f"""# Template Documentation Index

Generated on: {datetime.now().isoformat()}

## Templates

"""
        
        template_docs = []
        
        for template_path in template_list:
            print(f"Generating docs for: {os.path.relpath(template_path, self.base_path)}")
            
            try:
                template_info = self.extract_template_info(template_path)
                doc_content = self.generate_markdown_doc(template_info)
                
                # Create safe filename
                safe_name = template_info['name'].replace('/', '_').replace('.j2', '.md')
                doc_file = output_path / safe_name
                
                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                
                template_docs.append({
                    "name": template_info['name'],
                    "doc_file": safe_name,
                    "variables": len(template_info['variables']),
                    "blocks": len(template_info['blocks']),
                    "macros": len(template_info['macros']),
                    "size": template_info['size']
                })
                
                # Add to index
                index_content += f"- [{template_info['name']}]({safe_name}) "
                index_content += f"({len(template_info['variables'])} vars, "
                index_content += f"{len(template_info['blocks'])} blocks, "
                index_content += f"{template_info['size']} bytes)\n"
                
            except Exception as e:
                print(f"Error processing {template_path}: {e}")
                index_content += f"- {os.path.relpath(template_path, self.base_path)} - *Error: {e}*\n"
        
        # Write index
        with open(output_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # Generate summary JSON
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_templates": len(template_list),
            "successful_docs": len(template_docs),
            "templates": template_docs
        }
        
        with open(output_path / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nDocumentation generated in: {output_path}")
        print(f"Templates documented: {len(template_docs)}/{len(template_list)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate template documentation")
    parser.add_argument("--templates", required=True, help="File containing template list")
    parser.add_argument("--output", default="docs/templates", help="Output directory")
    parser.add_argument("--base-path", default=".", help="Base path for templates")
    
    args = parser.parse_args()
    
    # Read template list
    with open(args.templates, 'r') as f:
        templates = [line.strip() for line in f if line.strip()]
    
    # Generate documentation
    generator = TemplateDocGenerator(args.base_path)
    generator.generate_docs_for_templates(templates, args.output)

if __name__ == "__main__":
    main()
