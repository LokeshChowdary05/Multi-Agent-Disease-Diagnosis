# setup.py
# Quick setup script to help configure the environment

import os
import shutil

def create_env_file():
    """Create .env file from template"""
    
    print("🔧 Setting up environment configuration...")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        choice = input("Do you want to overwrite it? (y/n): ").lower()
        if choice != 'y':
            print("Keeping existing .env file.")
            return False
    
    # Copy from template
    if os.path.exists('.env.example'):
        try:
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
            
            print("\n📝 Please edit the .env file and add your OpenAI API key:")
            print("1. Open .env file in a text editor")
            print("2. Replace 'your_openai_api_key_here' with your actual API key")
            print("3. Save the file")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating .env file: {str(e)}")
            return False
    else:
        print("❌ .env.example template not found!")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'openai',
        'pandas',
        'plotly',
        'pydantic',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run this command to install them:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed!")
        return True

def run_tests():
    """Run the test script"""
    
    print("\n🧪 Running system tests...")
    
    try:
        import test_system
        success = test_system.main()
        return success
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 Multi-Agent Disease Diagnosis System Setup")
    print("=" * 50)
    
    # Step 1: Create .env file
    env_created = create_env_file()
    
    # Step 2: Check dependencies
    deps_ok = check_dependencies()
    
    # Step 3: Run tests if everything is ok
    if deps_ok:
        tests_ok = run_tests()
    else:
        tests_ok = False
    
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"   Environment file: {'✅' if env_created else '❌'}")
    print(f"   Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"   System tests: {'✅' if tests_ok else '❌'}")
    
    if env_created and deps_ok and tests_ok:
        print("\n🎉 Setup complete! Your system is ready to use.")
        print("\nNext steps:")
        print("1. Edit the .env file with your OpenAI API key")
        print("2. Run: streamlit run app.py")
        print("3. Open your browser to http://localhost:8501")
    else:
        print("\n⚠️  Setup incomplete. Please address the issues above.")
        
        if not deps_ok:
            print("\nTo install dependencies:")
            print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
