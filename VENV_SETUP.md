# OMNI V4 - Virtual Environment Setup

## Environment Information

**Python Version**: 3.10.11
**Virtual Environment Location**: `C:\Users\Jorge Alexander\omni_v4\venv\`
**Created**: 2025-01-02
**Status**: Ready for development

## Activation Instructions

### Windows (Command Prompt)
```cmd
cd "C:\Users\Jorge Alexander\omni_v4"
venv\Scripts\activate
```

### Windows (PowerShell)
```powershell
cd "C:\Users\Jorge Alexander\omni_v4"
.\venv\Scripts\Activate.ps1
```

### Windows (Git Bash)
```bash
cd "C:\Users\Jorge Alexander\omni_v4"
source venv/Scripts/activate
```

## Installed Dependencies

### Production Dependencies
- **python-dotenv** 1.0.0 - Environment variable management
- **PyYAML** 6.0.1 - YAML configuration parsing
- **supabase** 2.3.0 - Supabase database client
- **pandas** 2.1.4 - Data manipulation (Toast CSV processing)

### Testing Dependencies
- **pytest** 7.4.3 - Test framework
- **pytest-cov** 4.1.0 - Coverage reporting
- **pytest-mock** 3.12.0 - Mocking utilities

### Development Tools
- **mypy** 1.7.1 - Static type checking
- **black** 23.12.0 - Code formatting
- **flake8** 6.1.0 - Linting
- **ipython** 8.18.1 - Interactive shell

## Quick Commands

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Code Quality
```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Install Package in Development Mode
```bash
pip install -e .
```

## Notes

- This virtual environment is **completely separate** from V3's dependencies
- All 68 packages installed successfully with no conflicts
- Core modules verified working: `yaml`, `supabase`, `pytest`, `pandas`, `dotenv`
- Environment is ready for Week 2 development tasks

## Troubleshooting

### If activation fails:
1. Ensure you're in the correct directory: `C:\Users\Jorge Alexander\omni_v4`
2. Check that `venv\Scripts\activate` exists
3. Try using the full path: `C:\Users\Jorge Alexander\omni_v4\venv\Scripts\activate`

### To recreate the environment:
```bash
# Remove existing venv
rm -rf venv

# Create new venv
python -m venv venv

# Activate and install
source venv/Scripts/activate  # or appropriate activation for your shell
pip install --upgrade pip
pip install -r requirements.txt
```
