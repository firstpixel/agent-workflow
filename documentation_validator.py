#!/usr/bin/env python3
"""
Documentation Validation for Agent Workflow Project
Checks documentation accuracy, completeness, and consistency with code.
"""

import os
import re
import ast
import inspect
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class DocumentationIssue:
    """Represents a documentation issue."""
    type: str  # 'missing', 'inaccurate', 'outdated', 'inconsistent'
    location: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class DocumentationValidator:
    """Validates project documentation against actual code."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.issues: List[DocumentationIssue] = []
        
    def add_issue(self, issue_type: str, location: str, description: str, severity: str = 'medium'):
        """Add a documentation issue."""
        issue = DocumentationIssue(issue_type, location, description, severity)
        self.issues.append(issue)
        
    def validate_readme(self) -> None:
        """Validate README.md content."""
        readme_path = os.path.join(self.project_root, "README.md")
        if not os.path.exists(readme_path):
            self.add_issue('missing', 'README.md', 'README.md file is missing', 'critical')
            return
            
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check for essential sections
        required_sections = [
            'overview', 'features', 'getting started', 'installation', 
            'usage', 'contributing', 'license'
        ]
        
        content_lower = content.lower()
        for section in required_sections:
            if section not in content_lower:
                self.add_issue('missing', 'README.md', f'Missing {section} section', 'medium')
        
        # Check code examples in README
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        for i, code_block in enumerate(code_blocks):
            try:
                ast.parse(code_block)
            except SyntaxError:
                self.add_issue('inaccurate', f'README.md code block {i+1}', 
                             'Code block contains syntax errors', 'high')
        
        # Check for outdated information
        if 'python -m venv venv' in content and 'pip install -r requirements.txt' in content:
            # Good - has proper setup instructions
            pass
        else:
            self.add_issue('missing', 'README.md', 'Missing proper Python setup instructions', 'medium')
            
    def validate_design_document(self) -> None:
        """Validate design_document.md content."""
        design_path = os.path.join(self.project_root, "design_document.md")
        if not os.path.exists(design_path):
            self.add_issue('missing', 'design_document.md', 'Design document is missing', 'high')
            return
            
        with open(design_path, 'r') as f:
            content = f.read()
        
        # Check for key architectural concepts mentioned in code
        expected_concepts = [
            'LLMAgent', 'EvolvingAgent', 'WorkflowManager', 'MCSTExecutor',
            'MCST', 'Monte Carlo', 'evolution', 'branching'
        ]
        
        for concept in expected_concepts:
            if concept not in content:
                self.add_issue('missing', 'design_document.md', 
                             f'Missing documentation for {concept}', 'medium')
    
    def validate_code_documentation(self) -> None:
        """Validate docstrings and comments in Python files."""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            if '__pycache__' in root or '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            self._validate_python_file(file_path)
    
    def _validate_python_file(self, file_path: str) -> None:
        """Validate documentation in a single Python file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check module docstring
            if not ast.get_docstring(tree):
                self.add_issue('missing', file_path, 'Missing module docstring', 'low')
            
            # Check class and function docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        self.add_issue('missing', f'{file_path}:{node.lineno}', 
                                     f'Class {node.name} missing docstring', 'medium')
                
                elif isinstance(node, ast.FunctionDef):
                    if (node.name.startswith('_') and not node.name.startswith('__')):
                        continue  # Skip private methods
                    if not ast.get_docstring(node):
                        self.add_issue('missing', f'{file_path}:{node.lineno}', 
                                     f'Function {node.name} missing docstring', 'low')
        
        except Exception as e:
            self.add_issue('inaccurate', file_path, f'Error parsing file: {str(e)}', 'high')
    
    def validate_api_consistency(self) -> None:
        """Check if documented API matches actual implementation."""
        # Import the actual modules to check their interfaces
        try:
            from Agent import LLMAgent, EvolvingAgent
            from WorkflowManager import WorkflowManager
            from task import Task
            from mcst_executor import MCSTExecutor
            
            # Check LLMAgent interface
            llm_methods = [method for method in dir(LLMAgent) if not method.startswith('_')]
            expected_methods = ['execute', 'validate', 'run_with_retries', 'receive_input']
            
            for method in expected_methods:
                if method not in llm_methods:
                    self.add_issue('inaccurate', 'Agent.py', 
                                 f'LLMAgent missing expected method: {method}', 'high')
            
            # Check WorkflowManager interface
            wm_methods = [method for method in dir(WorkflowManager) if not method.startswith('_')]
            expected_wm_methods = ['add_agent', 'run_workflow', 'run']
            
            for method in expected_wm_methods:
                if method not in wm_methods:
                    self.add_issue('inaccurate', 'WorkflowManager.py', 
                                 f'WorkflowManager missing expected method: {method}', 'high')
            
            # Check Task interface
            task_methods = [method for method in dir(Task) if not method.startswith('_')]
            expected_task_methods = ['to_dict', 'to_json', 'from_json']
            
            for method in expected_task_methods:
                if method not in task_methods:
                    self.add_issue('inaccurate', 'task.py', 
                                 f'Task missing expected method: {method}', 'medium')
                                 
        except ImportError as e:
            self.add_issue('inaccurate', 'API validation', 
                         f'Cannot import modules for API validation: {str(e)}', 'high')
    
    def validate_examples(self) -> None:
        """Validate that code examples in documentation actually work."""
        readme_path = os.path.join(self.project_root, "README.md")
        if not os.path.exists(readme_path):
            return
            
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Extract and test the main example from README
        example_pattern = r'```python\n(from WorkflowManager.*?manager\.run_workflow.*?)```'
        matches = re.findall(example_pattern, content, re.DOTALL)
        
        for i, example in enumerate(matches):
            try:
                # Create a test environment
                test_globals = {}
                
                # Try to execute the example
                exec(example, test_globals)
                
            except Exception as e:
                self.add_issue('inaccurate', f'README.md example {i+1}', 
                             f'Example code fails to execute: {str(e)}', 'high')
    
    def validate_file_structure(self) -> None:
        """Validate that documented file structure matches actual structure."""
        readme_path = os.path.join(self.project_root, "README.md")
        if not os.path.exists(readme_path):
            return
            
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check if README mentions key files that should exist
        key_files = [
            'Agent.py', 'WorkflowManager.py', 'main.py', 'requirements.txt',
            'task.py', 'tool_manager.py', 'mcst_executor.py'
        ]
        
        for file_name in key_files:
            file_path = os.path.join(self.project_root, file_name)
            if not os.path.exists(file_path):
                self.add_issue('inconsistent', 'File structure', 
                             f'Key file {file_name} is missing from project', 'high')
        
        # Check for tools directory
        tools_dir = os.path.join(self.project_root, 'tools')
        if not os.path.exists(tools_dir):
            self.add_issue('inconsistent', 'File structure', 
                         'Tools directory is missing', 'medium')
    
    def run_all_validations(self) -> Dict:
        """Run all documentation validations."""
        print("Validating Documentation...")
        print("=" * 40)
        
        self.validate_readme()
        self.validate_design_document()
        self.validate_code_documentation()
        self.validate_api_consistency()
        self.validate_examples()
        self.validate_file_structure()
        
        # Categorize issues by severity
        critical = [i for i in self.issues if i.severity == 'critical']
        high = [i for i in self.issues if i.severity == 'high']
        medium = [i for i in self.issues if i.severity == 'medium']
        low = [i for i in self.issues if i.severity == 'low']
        
        report = {
            'total_issues': len(self.issues),
            'critical': len(critical),
            'high': len(high),
            'medium': len(medium),
            'low': len(low),
            'issues': [
                {
                    'type': issue.type,
                    'location': issue.location,
                    'description': issue.description,
                    'severity': issue.severity
                }
                for issue in self.issues
            ]
        }
        
        return report
    
    def print_summary(self, report: Dict) -> None:
        """Print documentation validation summary."""
        print(f"\nDocumentation Validation Results:")
        print(f"Total Issues: {report['total_issues']}")
        print(f"Critical: {report['critical']}")
        print(f"High: {report['high']}")
        print(f"Medium: {report['medium']}")
        print(f"Low: {report['low']}")
        
        if self.issues:
            print("\nIssues by Category:")
            for severity in ['critical', 'high', 'medium', 'low']:
                issues = [i for i in self.issues if i.severity == severity]
                if issues:
                    print(f"\n{severity.upper()} Issues:")
                    for issue in issues:
                        print(f"  - {issue.location}: {issue.description}")


def main():
    """Main documentation validation entry point."""
    validator = DocumentationValidator()
    report = validator.run_all_validations()
    validator.print_summary(report)
    
    # Save report
    import json
    with open("documentation_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: documentation_validation_report.json")
    
    return 0 if report['critical'] == 0 and report['high'] == 0 else 1


if __name__ == "__main__":
    exit(main())