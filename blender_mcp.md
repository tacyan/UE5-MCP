# Blender-MCP

## Overview
Blender-MCP is a module within the Model Context Protocol (MCP) that enables AI-driven automation in Blender. It facilitates scene generation, asset creation, texture application, and seamless integration with Unreal Engine 5 (UE5).

---

## **1. Features**
### **1.1 Procedural Scene Generation**
- Create complex scenes using natural language commands.
- Example:
  ```bash
  mcp.generate_scene "A sci-fi spaceship interior with neon lighting."
  ```

### **1.2 Asset Management & Texturing**
- Add, modify, and export assets efficiently.
- Example:
  ```bash
  mcp.add_object "chair" 2.5 3.0 0.0
  mcp.generate_texture "chair" "leather upholstery"
  ```

### **1.3 AI-Assisted Optimization**
- Automates LOD generation for performance optimization.
- Example:
  ```bash
  mcp.optimize_asset "building_model" --lod 3
  ```

---

## **2. Installation & Setup**
### **2.1 Prerequisites**
- Blender 3.x or later.
- Required add-ons enabled (`Node Wrangler`, `Blender Python API`).
- Install dependencies:
  ```bash
  pip install numpy scipy pillow requests
  ```

### **2.2 Loading MCP in Blender**
1. Open Blender.
2. Navigate to `Edit` → `Preferences` → `Add-ons`.
3. Enable the MCP plugin.
4. Restart Blender to apply changes.

---

## **3. Exporting to Unreal Engine 5**
### **3.1 Export Supported Formats**
- `.fbx`, `.obj`, `.gltf` formats are supported.
- Example:
  ```bash
  mcp.export_asset "tree_model" "fbx" "./exports/tree.fbx"
  ```

### **3.2 Asset Optimization Before Export**
- Reduce polycount for better performance:
  ```bash
  mcp.optimize_asset "tree_model" --polycount 5000
  ```

For more details on automation, refer to `automation.md`.

