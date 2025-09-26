#!/usr/bin/env python3
"""
Phase 2A Consolidation Matrix Generator
Analyzes all branches and creates comprehensive consolidation mapping
"""

import subprocess
import json
import csv
import os
from datetime import datetime
from collections import defaultdict

class ConsolidationAnalyzer:
    def __init__(self):
        self.branches = []
        self.consolidate_branches = []
        self.keep_branches = []
        self.analysis_results = {}
        
        # Define branch categorization rules based on Phase 1 results
        self.consolidate_patterns = [
            'phase-', 'sprint', 'feature/', 'feat/', 'env-inventories',
            'doc-refactor', 'phase2-', 'phase3', 'phase4'
        ]
        
        self.keep_patterns = [
            'main', 'phase-1.0-deployment', 'emergency-security',
            'hotfix/', 'fix/', 'audit-fixes', 'phase1a-safety',
            'phase1b-remediation', 'remediat'
        ]
        
        # Target branch mapping
        self.target_mapping = {
            'phase-2-consolidated': ['phase-', 'sprint'],
            'feature-consolidated-production': ['feature/', 'feat/'],
            'security-remediation-consolidated': ['security', 'remediat', 'fix/'],
            'infrastructure-consolidated': ['env-inventories', 'inventory']
        }

    def get_all_branches(self):
        """Get all remote branches"""
        try:
            result = subprocess.run(['git', 'branch', '-r'], 
                                  capture_output=True, text=True, check=True)
            branches = []
            for line in result.stdout.strip().split('\n'):
                branch = line.strip()
                if branch and not branch.startswith('origin/HEAD'):
                    branch_name = branch.replace('origin/', '')
                    branches.append(branch_name)
            return sorted(branches)
        except subprocess.CalledProcessError as e:
            print(f"Error getting branches: {e}")
            return []

    def categorize_branch(self, branch):
        """Categorize branch as CONSOLIDATE or KEEP"""
        branch_lower = branch.lower()
        
        # Check KEEP patterns first (higher priority)
        for pattern in self.keep_patterns:
            if pattern in branch_lower:
                return 'KEEP'
        
        # Check CONSOLIDATE patterns
        for pattern in self.consolidate_patterns:
            if pattern in branch_lower:
                return 'CONSOLIDATE'
        
        # Default to CONSOLIDATE for analysis
        return 'CONSOLIDATE'

    def get_target_branch(self, branch):
        """Determine target consolidation branch"""
        branch_lower = branch.lower()
        
        # Phase/Sprint branches
        if any(p in branch_lower for p in ['phase-', 'sprint']):
            return 'phase-2-consolidated'
        
        # Feature branches
        if any(p in branch_lower for p in ['feature/', 'feat/']):
            return 'feature-consolidated-production'
        
        # Security/Remediation branches
        if any(p in branch_lower for p in ['security', 'remediat', 'fix/']):
            return 'security-remediation-consolidated'
        
        # Infrastructure branches
        if any(p in branch_lower for p in ['env-inventories', 'inventory', 'vars']):
            return 'infrastructure-consolidated'
        
        # Default fallback
        return 'phase-2-consolidated'

    def analyze_branch_changes(self, branch):
        """Analyze what files/directories a branch modifies"""
        try:
            # Get diff from main branch
            result = subprocess.run(['git', 'diff', '--name-only', 'main', f'origin/{branch}'],
                                  capture_output=True, text=True, check=True)
            
            changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
            # Categorize changes by Ansible hierarchy
            categories = {
                'inventory': [],
                'roles': [],
                'playbooks': [],
                'vars': [],
                'templates': [],
                'files': [],
                'docs': [],
                'config': [],
                'other': []
            }
            
            for file_path in changed_files:
                if file_path.startswith('inventory/') or file_path.startswith('inventories/'):
                    categories['inventory'].append(file_path)
                elif file_path.startswith('roles/'):
                    categories['roles'].append(file_path)
                elif file_path.startswith('playbooks/'):
                    categories['playbooks'].append(file_path)
                elif file_path.startswith('vars/') or file_path.startswith('group_vars/') or file_path.startswith('host_vars/'):
                    categories['vars'].append(file_path)
                elif file_path.startswith('templates/'):
                    categories['templates'].append(file_path)
                elif file_path.startswith('files/'):
                    categories['files'].append(file_path)
                elif file_path.startswith('docs/'):
                    categories['docs'].append(file_path)
                elif file_path in ['ansible.cfg', '.ansible-lint', '.yamllint', 'requirements.yml']:
                    categories['config'].append(file_path)
                else:
                    categories['other'].append(file_path)
            
            return categories, len(changed_files)
            
        except subprocess.CalledProcessError:
            return {}, 0

    def assess_merge_conflicts(self, branch, target_branch):
        """Assess potential merge conflicts"""
        try:
            # Check if branches can merge cleanly
            result = subprocess.run(['git', 'merge-tree', 'main', f'origin/{branch}', f'origin/{target_branch}'],
                                  capture_output=True, text=True)
            
            conflict_level = 'LOW'
            if result.returncode != 0 or 'conflict' in result.stdout.lower():
                conflict_level = 'HIGH'
            elif len(result.stdout.strip()) > 100:  # Significant changes
                conflict_level = 'MEDIUM'
            
            return conflict_level
            
        except subprocess.CalledProcessError:
            return 'UNKNOWN'

    def get_branch_info(self, branch):
        """Get additional branch information"""
        try:
            # Get last commit info
            result = subprocess.run(['git', 'log', '-1', '--format=%H|%an|%ad|%s', f'origin/{branch}'],
                                  capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                commit_hash, author, date, message = result.stdout.strip().split('|', 3)
                return {
                    'last_commit': commit_hash[:8],
                    'author': author,
                    'last_modified': date,
                    'last_message': message[:50] + '...' if len(message) > 50 else message
                }
        except:
            pass
        
        return {
            'last_commit': 'unknown',
            'author': 'unknown',
            'last_modified': 'unknown',
            'last_message': 'unknown'
        }

    def generate_analysis(self):
        """Generate comprehensive branch analysis"""
        print("🔍 Analyzing repository branches...")
        
        self.branches = self.get_all_branches()
        print(f"Found {len(self.branches)} branches")
        
        analysis_data = []
        
        for branch in self.branches:
            print(f"Analyzing branch: {branch}")
            
            category = self.categorize_branch(branch)
            target_branch = self.get_target_branch(branch) if category == 'CONSOLIDATE' else 'N/A'
            
            # Analyze changes
            changes, file_count = self.analyze_branch_changes(branch)
            
            # Assess conflicts
            conflict_level = 'N/A'
            if category == 'CONSOLIDATE':
                conflict_level = self.assess_merge_conflicts(branch, target_branch)
            
            # Get branch info
            branch_info = self.get_branch_info(branch)
            
            # Determine dependencies based on Ansible hierarchy
            dependencies = []
            if changes.get('inventory'):
                dependencies.append('inventory-first')
            if changes.get('roles'):
                dependencies.append('roles-after-inventory')
            if changes.get('playbooks'):
                dependencies.append('playbooks-after-roles')
            
            analysis_data.append({
                'branch_name': branch,
                'category': category,
                'target_branch': target_branch,
                'file_count': file_count,
                'conflict_level': conflict_level,
                'dependencies': ', '.join(dependencies) if dependencies else 'none',
                'inventory_changes': len(changes.get('inventory', [])),
                'role_changes': len(changes.get('roles', [])),
                'playbook_changes': len(changes.get('playbooks', [])),
                'vars_changes': len(changes.get('vars', [])),
                'docs_changes': len(changes.get('docs', [])),
                'config_changes': len(changes.get('config', [])),
                'other_changes': len(changes.get('other', [])),
                'last_commit': branch_info['last_commit'],
                'author': branch_info['author'],
                'last_modified': branch_info['last_modified'],
                'last_message': branch_info['last_message']
            })
            
            if category == 'CONSOLIDATE':
                self.consolidate_branches.append(branch)
            else:
                self.keep_branches.append(branch)
        
        return analysis_data

    def generate_consolidation_matrix_csv(self, analysis_data):
        """Generate CSV consolidation matrix"""
        csv_file = 'docs/phase-2A/consolidation_matrix.csv'
        
        with open(csv_file, 'w', newline='') as f:
            fieldnames = [
                'branch_name', 'category', 'target_branch', 'file_count', 
                'conflict_level', 'dependencies', 'inventory_changes', 
                'role_changes', 'playbook_changes', 'vars_changes', 
                'docs_changes', 'config_changes', 'other_changes',
                'last_commit', 'author', 'last_modified', 'last_message'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analysis_data)
        
        print(f"✅ Generated consolidation matrix: {csv_file}")
        return csv_file

    def generate_consolidation_matrix_md(self, analysis_data):
        """Generate Markdown consolidation matrix"""
        md_file = 'docs/phase-2A/consolidation_matrix.md'
        
        with open(md_file, 'w') as f:
            f.write("# Phase 2A Consolidation Matrix\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary statistics
            consolidate_count = len([b for b in analysis_data if b['category'] == 'CONSOLIDATE'])
            keep_count = len([b for b in analysis_data if b['category'] == 'KEEP'])
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Branches**: {len(analysis_data)}\n")
            f.write(f"- **CONSOLIDATE**: {consolidate_count}\n")
            f.write(f"- **KEEP**: {keep_count}\n\n")
            
            # Target branch distribution
            target_dist = defaultdict(int)
            for branch in analysis_data:
                if branch['category'] == 'CONSOLIDATE':
                    target_dist[branch['target_branch']] += 1
            
            f.write("## Target Branch Distribution\n\n")
            for target, count in sorted(target_dist.items()):
                f.write(f"- **{target}**: {count} branches\n")
            f.write("\n")
            
            # Consolidation table
            f.write("## Consolidation Matrix\n\n")
            f.write("| Branch | Category | Target | Files | Conflicts | Dependencies | Inventory | Roles | Playbooks | Last Modified |\n")
            f.write("|--------|----------|--------|-------|-----------|--------------|-----------|-------|-----------|---------------|\n")
            
            for branch in sorted(analysis_data, key=lambda x: (x['category'], x['branch_name'])):
                f.write(f"| {branch['branch_name']} | {branch['category']} | {branch['target_branch']} | "
                       f"{branch['file_count']} | {branch['conflict_level']} | {branch['dependencies']} | "
                       f"{branch['inventory_changes']} | {branch['role_changes']} | {branch['playbook_changes']} | "
                       f"{branch['last_modified'][:10] if branch['last_modified'] != 'unknown' else 'unknown'} |\n")
            
            f.write("\n")
            
            # Detailed analysis by target branch
            f.write("## Detailed Analysis by Target Branch\n\n")
            
            for target in sorted(target_dist.keys()):
                target_branches = [b for b in analysis_data if b['target_branch'] == target]
                f.write(f"### {target}\n\n")
                f.write(f"**Branches to consolidate**: {len(target_branches)}\n\n")
                
                for branch in target_branches:
                    f.write(f"#### {branch['branch_name']}\n")
                    f.write(f"- **Files changed**: {branch['file_count']}\n")
                    f.write(f"- **Conflict level**: {branch['conflict_level']}\n")
                    f.write(f"- **Dependencies**: {branch['dependencies']}\n")
                    f.write(f"- **Last commit**: {branch['last_commit']} by {branch['author']}\n")
                    f.write(f"- **Last message**: {branch['last_message']}\n")
                    f.write(f"- **Changes breakdown**: Inventory({branch['inventory_changes']}), "
                           f"Roles({branch['role_changes']}), Playbooks({branch['playbook_changes']}), "
                           f"Vars({branch['vars_changes']}), Docs({branch['docs_changes']})\n\n")
        
        print(f"✅ Generated consolidation matrix: {md_file}")
        return md_file

def main():
    analyzer = ConsolidationAnalyzer()
    analysis_data = analyzer.generate_analysis()
    
    # Generate outputs
    csv_file = analyzer.generate_consolidation_matrix_csv(analysis_data)
    md_file = analyzer.generate_consolidation_matrix_md(analysis_data)
    
    print(f"\n🎯 Analysis Complete!")
    print(f"📊 CONSOLIDATE branches: {len(analyzer.consolidate_branches)}")
    print(f"🔒 KEEP branches: {len(analyzer.keep_branches)}")
    print(f"📁 Files generated: {csv_file}, {md_file}")

if __name__ == "__main__":
    main()
