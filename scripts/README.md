# Scripts Directory

This directory contains utility scripts for development, testing, and debugging of the OpenRouter Anthropic Server.

## 📋 **Available Scripts**

### 🧪 **test_phase1_implementation.py**
**Purpose**: Validates Phase 1 Claude Code implementation components

**Usage**:
```bash
# Run from project root
python scripts/test_phase1_implementation.py

# Or from src directory for proper import context
cd src && python ../scripts/test_phase1_implementation.py
```

**What it tests**:
- ✅ Enhanced Schema Converter (6 models supported)
- ✅ Tool Execution Service (15 tools configured)
- ✅ Reasoning Content Service (4 reasoning profiles)
- ✅ Enhanced Conversion Flow (overall readiness)
- ✅ Health Monitoring Endpoints (4 endpoints)

**When to use**:
- After system updates or changes
- To verify Phase 1 implementation status
- For system readiness validation
- During troubleshooting

### 🔍 **check_debug_logs.py**
**Purpose**: Debug utility for checking error logs via API endpoints

**Usage**:
```bash
# Check recent errors and statistics (requires running server)
python scripts/check_debug_logs.py

# Check specific error by correlation ID
python scripts/check_debug_logs.py f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation
```

**Features**:
- 📊 Recent error analysis with detailed context
- 📈 Error statistics and trends
- 🔍 Specific error lookup by correlation ID
- 📋 Service and endpoint error categorization

**API Endpoints Used**:
- `GET /debug/errors/recent?count=N` - Recent errors
- `GET /debug/errors/stats` - Error statistics  
- `GET /debug/errors/{correlation_id}` - Specific error lookup

**When to use**:
- Following "Critical Development Rule #3: CHECK DEBUG LOGS FIRST"
- When investigating errors or issues
- For error trend analysis
- During system monitoring

## 🚀 **Usage Guidelines**

### **System Validation Workflow**
1. **Start Server**: Ensure the OpenRouter Anthropic Server is running
2. **Validate Implementation**: Run `test_phase1_implementation.py`
3. **Check for Issues**: Use `check_debug_logs.py` if any problems arise

### **Debugging Workflow**
1. **Error Occurs**: Note any error messages or correlation IDs
2. **Check Debug Logs**: Run `check_debug_logs.py` immediately
3. **Analyze Patterns**: Review error statistics and trends
4. **Specific Investigation**: Use correlation ID for detailed error analysis

## 📁 **Script Requirements**

- **Python 3.10+** required
- **Server Running** (for debug log checker)
- **Dependencies**: All scripts use existing project dependencies
- **Permissions**: Scripts require read access to project modules

## 🔧 **Development Notes**

These scripts are maintained as development and operational utilities. They provide valuable insights into system health and implementation status without requiring external tools or complex setup.

Both scripts are referenced in the project documentation and serve ongoing operational needs rather than one-time setup tasks. 