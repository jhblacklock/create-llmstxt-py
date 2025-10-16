#!/usr/bin/env python3
"""Test YAML functionality"""

try:
    import yaml
    print("✅ PyYAML imported successfully")
    
    # Test reading the YAML file
    with open('urls/llms_urls.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"✅ YAML file loaded successfully")
    print(f"📊 Sections found: {len(data.get('sections', []))}")
    
    # Test the generator
    from generate_llmstxt import SimpleLLMsTextGenerator
    generator = SimpleLLMsTextGenerator()
    
    # Test YAML reading
    yaml_data = generator.read_urls_from_yaml('urls/llms_urls.yaml')
    print(f"✅ Generator YAML reading successful")
    print(f"📊 Type: {type(yaml_data)}")
    
    if isinstance(yaml_data, dict) and 'sections' in yaml_data:
        print(f"📊 Sections: {len(yaml_data['sections'])}")
        for i, section in enumerate(yaml_data['sections'][:3]):  # Show first 3 sections
            print(f"  {i+1}. {section.get('header', 'Unknown')}: {len(section.get('urls', []))} URLs")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
