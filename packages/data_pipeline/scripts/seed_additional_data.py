"""
Seed Additional Data
Runs both knowledge base and audit logs seeding
"""

import subprocess
import sys
import os

def run_script(script_name):
    """Run a Python script"""
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print('='*60)
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    
    if result.returncode == 0:
        print(f"✓ {script_name} completed successfully")
        return True
    else:
        print(f"❌ {script_name} failed")
        return False

def main():
    print("="*60)
    print("SEEDING ADDITIONAL DATA")
    print("="*60)
    print("\nThis will populate:")
    print("1. Knowledge Base Documents (for RAG)")
    print("2. Agent Audit Logs (for demonstration)")
    print("="*60)
    
    # Run knowledge base seeding
    kb_success = run_script("seed_knowledge_base.py")
    
    # Run audit logs seeding
    logs_success = run_script("seed_audit_logs.py")
    
    # Summary
    print("\n" + "="*60)
    print("SEEDING SUMMARY")
    print("="*60)
    print(f"Knowledge Base: {'✓ Success' if kb_success else '❌ Failed'}")
    print(f"Audit Logs: {'✓ Success' if logs_success else '❌ Failed'}")
    print("="*60)
    
    if kb_success and logs_success:
        print("\n✓ ALL DATA SEEDED SUCCESSFULLY!")
    else:
        print("\n⚠ Some seeding operations failed")

if __name__ == "__main__":
    main()
