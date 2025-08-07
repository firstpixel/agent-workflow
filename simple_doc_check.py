#!/usr/bin/env python3
"""
Simple Documentation Checker for Agent Workflow Project
"""

import os
import re
import ast
from typing import List

def check_documentation():
    """Check documentation completeness and accuracy."""
    issues = []
    
    # Check README.md
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        # Check for essential sections
        required_sections = ['overview', 'features', 'getting started', 'installation']
        content_lower = readme_content.lower()
        
        missing_sections = [s for s in required_sections if s not in content_lower]
        if missing_sections:
            issues.append(f"README missing sections: {', '.join(missing_sections)}")
        
        # Check code examples syntax
        code_blocks = re.findall(r'```python\n(.*?)```', readme_content, re.DOTALL)
        for i, code_block in enumerate(code_blocks):
            try:
                ast.parse(code_block)
            except SyntaxError as e:
                issues.append(f"README code block {i+1} has syntax error: {str(e)}")
    else:
        issues.append("README.md is missing")
    
    # Check design document
    design_path = "design_document.md"
    if os.path.exists(design_path):
        with open(design_path, 'r') as f:
            design_content = f.read()
        
        # Check for key concepts
        key_concepts = ['LLMAgent', 'EvolvingAgent', 'WorkflowManager', 'MCST', 'evolution']
        missing_concepts = [c for c in key_concepts if c not in design_content]
        if missing_concepts:
            issues.append(f"Design doc missing concepts: {', '.join(missing_concepts)}")
    else:
        issues.append("design_document.md is missing")
    
    # Check Python files for docstrings
    python_files = ['Agent.py', 'WorkflowManager.py', 'main.py', 'task.py', 'mcst_executor.py']
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                # Check module docstring
                if not ast.get_docstring(tree):
                    issues.append(f"{file_path} missing module docstring")
                
                # Count classes and functions without docstrings
                missing_docstrings = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        if not node.name.startswith('_') and not ast.get_docstring(node):
                            missing_docstrings += 1
                
                if missing_docstrings > 0:
                    issues.append(f"{file_path} has {missing_docstrings} classes/functions without docstrings")
                    
            except Exception as e:
                issues.append(f"Error parsing {file_path}: {str(e)}")
        else:
            issues.append(f"Key file {file_path} is missing")
    
    # Check file structure
    expected_files = ['requirements.txt', 'tools/', 'LICENSE']
    for item in expected_files:
        if not os.path.exists(item):
            issues.append(f"Missing {item}")
    
    return issues

def main():
    """Main entry point."""
    print("Documentation Validation Report")
    print("=" * 40)
    
    issues = check_documentation()
    
    if not issues:
        print("✓ All documentation checks passed!")
        return 0
    else:
        print(f"Found {len(issues)} documentation issues:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        return 1

if __name__ == "__main__":
    exit(main())