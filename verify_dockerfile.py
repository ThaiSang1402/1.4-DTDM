#!/usr/bin/env python3
"""
Verify Dockerfile exists and is readable for Render deployment.
"""

import os
import sys

def verify_dockerfile():
    """Verify Dockerfile files exist and are readable."""
    print("🔍 Verifying Dockerfile files for Render...")
    
    files_to_check = [
        "Dockerfile",
        "Dockerfile.aiserver", 
        "render.yaml"
    ]
    
    all_good = True
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"✅ {filename}: EXISTS ({len(content)} chars)")
                    
                    # Check for key content
                    if filename == "Dockerfile":
                        if "FROM python:" in content and "scalable_ai_api.load_balancer.render_app:app" in content:
                            print(f"   ✅ {filename}: Content looks correct")
                        else:
                            print(f"   ❌ {filename}: Content may be incorrect")
                            all_good = False
                    
                    elif filename == "Dockerfile.aiserver":
                        if "FROM python:" in content and "scalable_ai_api.ai_server.render_app:app" in content:
                            print(f"   ✅ {filename}: Content looks correct")
                        else:
                            print(f"   ❌ {filename}: Content may be incorrect")
                            all_good = False
                    
                    elif filename == "render.yaml":
                        if "dockerfilePath: Dockerfile" in content and "dockerfilePath: Dockerfile.aiserver" in content:
                            print(f"   ✅ {filename}: Paths look correct")
                        else:
                            print(f"   ❌ {filename}: Paths may be incorrect")
                            all_good = False
                            
            except Exception as e:
                print(f"❌ {filename}: Error reading file - {e}")
                all_good = False
        else:
            print(f"❌ {filename}: FILE NOT FOUND")
            all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("✅ All Dockerfile verification passed!")
        print("🚀 Ready for Render deployment")
    else:
        print("❌ Some issues found. Check errors above.")
    
    return all_good

if __name__ == "__main__":
    success = verify_dockerfile()
    sys.exit(0 if success else 1)