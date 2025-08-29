# scripts/validate_setup.py

import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists"""
    if Path(".env").exists():
        return True, "✅ .env file found"
    else:
        return False, "❌ .env file not found. Run: cp .env.example .env"

def check_required_keys() -> Tuple[bool, Dict[str, bool]]:
    """Check if required API keys are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = {
        "OPENAI_API_KEY": "OpenAI (Required for agents)",
        "PERPLEXITY_API_KEY": "Perplexity (Required for research)",
        "SUPABASE_URL": "Supabase URL (Required for database)",
        "SUPABASE_SERVICE_KEY": "Supabase Key (Required for database)",
    }
    
    optional_keys = {
        "FACEBOOK_ACCESS_TOKEN": "Facebook (Optional for posting)",
        "INSTAGRAM_ACCESS_TOKEN": "Instagram (Optional for posting)",
        "WHATSAPP_BUSINESS_API_KEY": "WhatsApp (Optional for messaging)",
        "WOMPI_PUBLIC_KEY": "Wompi (Optional for payments)",
    }
    
    results = {}
    all_required_present = True
    
    print("\n📋 Required API Keys:")
    for key, description in required_keys.items():
        value = os.getenv(key, "")
        is_set = len(value) > 0 and not value.startswith("your-") and not value.startswith("sk-your")
        results[key] = is_set
        
        if is_set:
            # Mask the key for security
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  ✅ {description}: {masked}")
        else:
            print(f"  ❌ {description}: Not configured")
            all_required_present = False
    
    print("\n📋 Optional API Keys:")
    for key, description in optional_keys.items():
        value = os.getenv(key, "")
        is_set = len(value) > 0 and not value.startswith("your-") and not value.startswith("sk-your")
        results[key] = is_set
        
        if is_set:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  ✅ {description}: {masked}")
        else:
            print(f"  ⚠️  {description}: Not configured (optional)")
    
    return all_required_present, results

def check_dependencies() -> Tuple[bool, str]:
    """Check if Python dependencies are installed"""
    try:
        import langchain
        import fastapi
        import supabase
        import openai
        return True, "✅ Core dependencies installed"
    except ImportError as e:
        return False, f"❌ Missing dependency: {e.name}. Run: pip install -r requirements.txt"

def check_supabase_connection() -> Tuple[bool, str]:
    """Test Supabase connection"""
    try:
        from database.supabase_client import SupabaseClient
        client = SupabaseClient()
        return True, "✅ Supabase connection successful"
    except Exception as e:
        return False, f"❌ Supabase connection failed: {str(e)}"

def check_directories() -> Tuple[bool, str]:
    """Check if required directories exist"""
    required_dirs = ["logs", "prompts/templates"]
    missing = []
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        return False, f"❌ Missing directories: {', '.join(missing)}"
    return True, "✅ All directories present"

def main():
    print("\n" + "=" * 60)
    print("🔍 Ghost Kitchen AI Platform - Setup Validation")
    print("=" * 60)
    
    all_good = True
    
    # Check environment file
    success, message = check_env_file()
    print(f"\n{message}")
    all_good = all_good and success
    
    if not success:
        print("\n⚠️  Please create .env file first:")
        print("   cp .env.example .env")
        print("   Then edit .env with your API keys")
        return
    
    # Check dependencies
    success, message = check_dependencies()
    print(f"\n{message}")
    all_good = all_good and success
    
    # Check directories
    success, message = check_directories()
    print(f"{message}")
    all_good = all_good and success
    
    # Check API keys
    success, results = check_required_keys()
    all_good = all_good and success
    
    # Test Supabase if keys are present
    if results.get("SUPABASE_URL") and results.get("SUPABASE_SERVICE_KEY"):
        success, message = check_supabase_connection()
        print(f"\n{message}")
        all_good = all_good and success
    
    # Final verdict
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All required components are configured!")
        print("\nYou can now run:")
        print("  python scripts/start_platform.py")
        print("\nOr start the API server:")
        print("  python main.py")
    else:
        print("⚠️  Some components need configuration")
        print("\nMinimum requirements to start:")
        print("1. Configure OPENAI_API_KEY in .env")
        print("2. Configure PERPLEXITY_API_KEY in .env")
        print("3. Configure Supabase credentials in .env")
        print("4. Run: pip install -r requirements.txt")
        
        print("\n💡 Tip: You can still test without all social media APIs")
        print("   The system will skip platforms that aren't configured")

if __name__ == "__main__":
    main()