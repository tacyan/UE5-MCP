# MCP Commands

## Overview
This document provides a list of available commands and parameters used for controlling Blender-MCP and Unreal Engine 5-MCP. These commands help automate tasks related to scene generation, asset management, level design, and debugging.

---

## **1. Blender-MCP Commands**
### **1.1 Scene Generation**
#### `mcp.generate_scene "description"`
- **Description**: Generates a new scene based on a natural language description.
- **Example**:
  ```bash
  mcp.generate_scene "A futuristic city with neon lights and flying cars."
  ```

#### `mcp.add_object "object_type" x y z`
- **Description**: Adds a specific object to the active scene at the given coordinates.
- **Example**:
  ```bash
  mcp.add_object "tree" 5.0 2.5 0.0
  ```

### **1.2 Asset Management**
#### `mcp.generate_texture "object_name" "texture_type"`
- **Description**: Generates and applies a texture to an object.
- **Example**:
  ```bash
  mcp.generate_texture "rock_model" "mossy stone"
  ```

#### `mcp.export_asset "object_name" "format" "filepath"`
- **Description**: Exports an asset in the specified format.
- **Example**:
  ```bash
  mcp.export_asset "car_model" "fbx" "./exports/car_model.fbx"
  ```

---

## **2. Unreal Engine 5-MCP Commands**
### **2.1 Level Design Automation**
#### `mcp.generate_terrain width height detail_level`
- **Description**: Creates procedural terrain with the given dimensions and detail level.
- **Example**:
  ```bash
  mcp.generate_terrain 1000 1000 "high"
  ```

#### `mcp.populate_level "asset_type" density`
- **Description**: Populates the level with a specified number of assets.
- **Example**:
  ```bash
  mcp.populate_level "trees" 500
  ```

### **2.2 Blueprint Automation**
#### `mcp.generate_blueprint "logic_description"`
- **Description**: Generates a Blueprint based on a natural language description.
- **Example**:
  ```bash
  mcp.generate_blueprint "A door that opens when the player interacts."
  ```

### **2.3 Debugging & Optimization**
#### `mcp.profile_performance "level_name"`
- **Description**: Analyzes level performance and provides optimization suggestions.
- **Example**:
  ```bash
  mcp.profile_performance "desert_map"
  ```

---

## **3. General MCP Commands**
#### `mcp.list_commands`
- **Description**: Displays a list of all available commands.
- **Example**:
  ```bash
  mcp.list_commands
  ```

#### `mcp.help "command_name"`
- **Description**: Provides details and usage examples for a specific command.
- **Example**:
  ```bash
  mcp.help "generate_blueprint"
  ```

For additional details on API functions, refer to `api_reference.md`.

