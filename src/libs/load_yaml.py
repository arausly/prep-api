"""Utility to load yaml files and pass parameters"""

import yaml


def load_yaml_with_vars(filepath, **kwargs):
    """Load Yaml files with parameters"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Replace placeholders with actual values
    content = content.format(**kwargs)
    return yaml.safe_load(content)
