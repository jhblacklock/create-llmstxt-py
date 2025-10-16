#!/usr/bin/env python3
"""Debug YAML parsing"""

import yaml
from generate_llmstxt import SimpleLLMsTextGenerator

print("Testing YAML parsing...")

try:
    generator = SimpleLLMsTextGenerator()
    yaml_data = generator.read_urls_from_yaml('urls/llms_urls.yaml')
    
    print(f"YAML data type: {type(yaml_data)}")
    
    if isinstance(yaml_data, list):
        print("Detected as flat YAML (file_urls)")
        print(f"Number of URLs: {len(yaml_data)}")
    elif isinstance(yaml_data, dict) and 'sections' in yaml_data:
        print("Detected as structured YAML (file_sections)")
        print(f"Number of sections: {len(yaml_data['sections'])}")
        for i, section in enumerate(yaml_data['sections'][:3]):
            print(f"  Section {i+1}: {section['header']} - {len(section['urls'])} URLs")
    else:
        print("Unknown YAML format")
        print(f"Keys: {list(yaml_data.keys()) if isinstance(yaml_data, dict) else 'Not a dict'}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
