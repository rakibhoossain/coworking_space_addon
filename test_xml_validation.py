#!/usr/bin/env python3
"""
Test script to validate XML files for Odoo 18 compatibility
"""

import xml.etree.ElementTree as ET
import os
import sys

def test_xml_files():
    """Test all XML files in the coworking_space module"""
    print("🔍 Testing XML files for Odoo 18 compatibility...")
    
    # Get the directory of this script
    module_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all XML files
    xml_files = []
    for root, dirs, files in os.walk(module_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    print(f"Found {len(xml_files)} XML files to test")
    
    errors = []
    deprecated_elements = []
    
    for xml_file in xml_files:
        try:
            # Parse XML
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Check for deprecated elements
            for elem in root.iter():
                if elem.tag == 'tree':
                    deprecated_elements.append(f"{xml_file}: Found deprecated <tree> element")
                
                # Check for deprecated attrs attribute
                if 'attrs' in elem.attrib:
                    deprecated_elements.append(f"{xml_file}: Found deprecated 'attrs' attribute in {elem.tag}")
            
            print(f"✅ {os.path.relpath(xml_file, module_dir)}")
            
        except ET.ParseError as e:
            error_msg = f"❌ {os.path.relpath(xml_file, module_dir)}: {e}"
            print(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"⚠️  {os.path.relpath(xml_file, module_dir)}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    # Report results
    print(f"\n📊 Test Results:")
    print(f"   Total files tested: {len(xml_files)}")
    print(f"   Errors: {len(errors)}")
    print(f"   Deprecated elements: {len(deprecated_elements)}")
    
    if errors:
        print(f"\n❌ Errors found:")
        for error in errors:
            print(f"   {error}")
    
    if deprecated_elements:
        print(f"\n⚠️  Deprecated elements found:")
        for dep in deprecated_elements:
            print(f"   {dep}")
    
    if not errors and not deprecated_elements:
        print(f"\n🎉 All XML files are valid and Odoo 18 compatible!")
        return True
    else:
        return False

if __name__ == "__main__":
    success = test_xml_files()
    sys.exit(0 if success else 1)
