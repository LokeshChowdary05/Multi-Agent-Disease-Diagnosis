# Troubleshooting Guide

## 🔧 Common Issues and Solutions

### 1. Function Not Defined Error

**Error:** `name 'simulate_diagnostic_process' is not defined`

**Solution:** 
✅ **FIXED** - This has been resolved by moving function definitions to the top of app.py

If you still see this error:
1. Make sure you're using the latest version of app.py
2. Restart your Streamlit application: `Ctrl+C` then `streamlit run app.py`

### 2. Import Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solutions:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually if needed
pip install streamlit openai pandas plotly pydantic python-dotenv
```

### 3. OpenAI API Issues

**Error:** `OpenAI API key not found` or `Invalid API key`

**Solutions:**
1. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and add your real API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. Verify your API key is correct:
   - Go to https://platform.openai.com/api-keys
   - Copy the correct key
   - Make sure there are no extra spaces

### 4. Port Already in Use

**Error:** `Port 8501 is already in use`

**Solutions:**
```bash
# Option 1: Use a different port
streamlit run app.py --server.port 8502

# Option 2: Kill the process using port 8501 (Windows)
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# Option 3: Kill the process using port 8501 (Mac/Linux)
lsof -ti:8501 | xargs kill -9
```

### 5. Streamlit Won't Start

**Solutions:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with debug flag
streamlit run app.py --logger.level debug

# Check if Python is in PATH
python --version
```

### 6. Demo Mode Not Working

**Error:** Agents don't respond in demo mode

**Solutions:**
1. Make sure "Demo Mode" checkbox is checked in the sidebar
2. Select a case from the dropdown
3. Click "Start Diagnostic Session"
4. Wait for the simulation to complete (takes about 6 seconds)

### 7. Real API Mode Issues

**Error:** API calls fail when demo mode is unchecked

**Solutions:**
1. Verify your OpenAI API key is set correctly in `.env`
2. Check your OpenAI account has sufficient credits
3. Make sure you have access to GPT-4 model
4. Start with demo mode to test the interface first

### 8. Virtual Environment Issues (Windows)

**Error:** `cannot be loaded because running scripts is disabled`

**Solutions:**
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use Command Prompt instead of PowerShell
cmd
venv\Scripts\activate.bat
```

### 9. Python Path Issues

**Error:** `Python is not recognized`

**Solutions:**
1. Add Python to PATH during installation
2. Or manually add Python to PATH:
   - Search "Environment Variables" in Windows Start menu
   - Edit system environment variables
   - Add Python installation path (usually C:\Python310\)

### 10. File Not Found Errors

**Error:** Various file not found errors

**Solutions:**
1. Make sure you're in the correct directory:
   ```bash
   cd "E:\Multi Agent Disease Diagnosis\medical-diagnosis-system"
   ```

2. Verify all files are present:
   ```bash
   python test_system.py
   ```

## 🚨 Emergency Solutions

### Complete Reset
If nothing works, try this complete reset:

1. **Delete and recreate virtual environment:**
   ```bash
   rmdir /s venv  # Windows
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Clean reinstall of dependencies:**
   ```bash
   pip uninstall -y -r requirements.txt
   pip install -r requirements.txt
   ```

3. **Reset Streamlit:**
   ```bash
   streamlit cache clear
   streamlit config show
   ```

### Quick Diagnostic Check
Run this quick check to identify issues:

```bash
# Test the system
python test_system.py

# Or run setup script
python setup.py
```

## 📞 Getting Help

### Step-by-Step Debugging

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **Test imports:**
   ```bash
   python -c "import streamlit; print('Streamlit OK')"
   python -c "import openai; print('OpenAI OK')"
   ```

3. **Verify file structure:**
   ```
   medical-diagnosis-system/
   ├── agents.py
   ├── orchestrator.py
   ├── medical_data.py
   ├── app.py
   ├── requirements.txt
   ├── .env (you create this)
   └── .env.example
   ```

4. **Check .env file:**
   ```bash
   type .env  # Windows
   cat .env   # Mac/Linux
   ```

### Error Log Collection

If you need help, collect this information:

1. **Python version:** `python --version`
2. **Error message:** Copy the full error from terminal
3. **Operating system:** Windows/Mac/Linux version
4. **Steps that led to error:** What you were trying to do

### Performance Issues

If the application is slow:

1. **Check system resources:** Ensure you have enough RAM (4GB+ recommended)
2. **Close other applications:** Free up system resources
3. **Use demo mode:** For testing without API calls
4. **Restart browser:** Clear browser cache

## ✅ Success Checklist

Your system is working correctly when:

- ✅ `python test_system.py` passes all tests
- ✅ `streamlit run app.py` starts without errors
- ✅ Browser opens to http://localhost:8501
- ✅ You can see the sidebar with case selection
- ✅ Demo mode runs diagnostic sessions
- ✅ You can select and run different cases

## 🔄 Regular Maintenance

### Weekly Tasks
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Clear Streamlit cache: `streamlit cache clear`
- Check for new medical data updates

### Monthly Tasks
- Rotate API keys for security
- Backup custom cases and configurations
- Review and update medical condition database

---

**Remember:** This system is for educational purposes only. Always validate any diagnostic outputs with qualified medical professionals.
