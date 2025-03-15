# MCP Troubleshooting Guide

## Overview
This document provides solutions for common issues encountered while using MCP with Blender and Unreal Engine 5 (UE5). If problems persist, consult the community forums or submit an issue on GitHub.

---

## **1. General Issues**
### **1.1 MCP Not Running**
#### **Possible Causes & Solutions**
- **Python not installed** → Ensure Python 3.x is installed.
  ```bash
  python --version
  ```
- **Missing dependencies** → Reinstall required packages.
  ```bash
  pip install -r requirements.txt
  ```
- **Incorrect configuration** → Check `mcp_config.json` for errors.

### **1.2 Command Not Found**
#### **Possible Causes & Solutions**
- Ensure MCP is installed and included in system `PATH`.
  ```bash
  echo $PATH
  ```
- If using a virtual environment, activate it:
  ```bash
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate  # Windows
  ```

---

## **2. Blender-Specific Issues**
### **2.1 Scene Not Generating**
#### **Possible Causes & Solutions**
- Check if Blender is running with the MCP plugin loaded.
- Ensure the `blender_mcp_config.json` file is correctly configured.
- Run the command in debug mode:
  ```bash
  mcp.generate_scene "A forest with a waterfall" --debug
  ```

### **2.2 Exported Assets Have Missing Textures**
#### **Possible Causes & Solutions**
- Ensure textures are packed before exporting:
  ```bash
  mcp.export_asset "house_model" "fbx" --include-textures
  ```
- Check the texture paths in Blender.

---

## **3. Unreal Engine 5-Specific Issues**
### **3.1 MCP Not Detected in UE5**
#### **Possible Causes & Solutions**
- Ensure UE5’s Python Editor Script Plugin is enabled.
  1. Go to `Edit` → `Plugins`
  2. Search for `Python Editor Script Plugin`
  3. Enable and restart UE5

### **3.2 Performance Bottlenecks in Level Design**
#### **Possible Causes & Solutions**
- Reduce object polycount using MCP’s LOD optimization:
  ```bash
  mcp.optimize_level --max-polycount 500000
  ```
- Disable real-time lighting in the config:
  ```json
  "dynamic_lighting": false
  ```

### **3.3 AI-Generated Blueprints Not Functioning**
#### **Possible Causes & Solutions**
- Check the generated Blueprint nodes for missing connections.
- Debug with:
  ```bash
  mcp.debug_blueprint "door_script"
  ```

---

## **4. AI Integration Issues**
### **4.1 AI Features Not Working**
#### **Possible Causes & Solutions**
- Verify that the AI provider is set correctly in `mcp_config.json`:
  ```json
  "provider": "openai"
  ```
- Ensure the API key is correct and valid.
- Check network connectivity.

---

## **5. Resetting MCP to Default**
If problems persist, reset MCP configurations:
```bash
mcp.reset_config
```

For additional help, refer to `configurations.md` or visit the support forum.

