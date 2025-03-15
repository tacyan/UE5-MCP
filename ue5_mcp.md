# Unreal Engine 5-MCP

## Overview
UE5-MCP is a module within the Model Context Protocol (MCP) that facilitates AI-assisted automation in Unreal Engine 5. It enhances level design, asset integration, Blueprint automation, and performance optimization.

---

## **1. Features**
### **1.1 Procedural Level Design**
- Generate environments using natural language commands.
- Example:
  ```bash
  mcp.generate_terrain 2000 2000 "high"
  ```

### **1.2 AI-Assisted Asset Population**
- Automatically places objects and optimizes layouts.
- Example:
  ```bash
  mcp.populate_level "rocks" 1000
  ```

### **1.3 Blueprint Automation**
- Creates and modifies gameplay logic automatically.
- Example:
  ```bash
  mcp.generate_blueprint "A door that opens when the player interacts."
  ```

### **1.4 Performance Profiling**
- Detects performance bottlenecks and suggests optimizations.
- Example:
  ```bash
  mcp.profile_performance "desert_map"
  ```

---

## **2. Installation & Setup**
### **2.1 Prerequisites**
- Unreal Engine 5.1 or later.
- Enable required UE5 plugins:
  - `Python Editor Script Plugin`
  - `Procedural Content Generation (PCG) Framework`

### **2.2 Installing MCP in UE5**
1. Open Unreal Engine 5.
2. Navigate to `Edit` → `Plugins`.
3. Enable MCP-related plugins.
4. Restart UE5 to apply changes.

---

## **3. Blender Integration**
### **3.1 Importing Blender Assets**
- Supports `.fbx`, `.obj`, `.gltf` formats.
- Example:
  ```bash
  mcp.import_asset "./exports/tree.fbx"
  ```

### **3.2 Automated Texture & Material Assignments**
- MCP assigns materials based on asset metadata.
- Example:
  ```bash
  mcp.apply_material "tree_model" "bark_texture"
  ```

For more details, refer to `blender_mcp.md` and `automation.md`.

