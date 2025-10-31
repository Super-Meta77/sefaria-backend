"""
Quick setup script for the Sefaria backend
Creates .env file and tests the configuration
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / 'env.example'
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example_path.exists():
        print("❌ env.example not found")
        return False
    
    # Copy env.example to .env
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print()
    print("⚠️  IMPORTANT: Edit backend/.env and add your OpenAI API key!")
    print("   Get your key from: https://platform.openai.com/api-keys")
    print()
    return True

def check_env():
    """Check if environment is properly configured"""
    print("=" * 70)
    print("🔍 Checking Environment Configuration")
    print("=" * 70)
    print()
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    checks = {}
    
    # Check Neo4j
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if neo4j_uri and neo4j_user and neo4j_password:
        checks["Neo4j"] = "✅ Configured"
        print(f"✅ Neo4j URI: {neo4j_uri}")
    else:
        checks["Neo4j"] = "❌ Missing credentials"
        print("❌ Neo4j credentials not set")
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key and openai_key != "sk-your-openai-api-key-here":
        checks["OpenAI"] = "✅ Configured"
        print(f"✅ OpenAI API key: {openai_key[:20]}...")
    else:
        checks["OpenAI"] = "⚠️  Not configured (AI features will not work)"
        print("⚠️  OpenAI API key not set - AI features disabled")
        print("   Get your key from: https://platform.openai.com/api-keys")
        print("   Edit backend/.env and replace 'sk-your-openai-api-key-here'")
    
    print()
    print("=" * 70)
    print("📊 Configuration Summary")
    print("=" * 70)
    for key, status in checks.items():
        print(f"{key}: {status}")
    print()
    
    return all("✅" in status for status in checks.values())

def main():
    print("=" * 70)
    print("🚀 Sefaria Backend Setup")
    print("=" * 70)
    print()
    
    # Step 1: Create .env file
    if not create_env_file():
        return
    
    # Step 2: Check environment
    all_configured = check_env()
    
    # Step 3: Instructions
    print("=" * 70)
    print("📝 Next Steps")
    print("=" * 70)
    print()
    
    if not all_configured:
        print("1. Edit backend/.env file")
        print("2. Add your OpenAI API key (get from https://platform.openai.com/api-keys)")
        print("3. Save the file")
        print("4. Run this script again to verify")
        print()
    else:
        print("✅ Configuration complete!")
        print()
        print("You can now:")
        print("1. Start the backend: uvicorn main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test AI features: python scripts/test_ai_features.py")
        print("4. Start embedding: python scripts/embed_texts.py")
        print()

if __name__ == "__main__":
    main()

