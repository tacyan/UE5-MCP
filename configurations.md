# MCP Configurations

## Overview
This document outlines the available configuration settings for the Model Context Protocol (MCP). These settings allow users to customize automation behavior, AI integration, asset processing, and performance optimizations.

---

## **1. General Configuration**
### **1.1 Configuration File Location**
The configuration file (`mcp_config.json`) is located in:
- **Blender:** `~/.mcp/blender_mcp_config.json`
- **Unreal Engine 5:** `~/.mcp/ue5_mcp_config.json`

### **1.2 Default Settings**
The default settings can be modified in the config file:
```json
{
  "ai_enabled": true,
  "default_export_format": "fbx",
  "logging_level": "INFO",
  "auto_update": true
}
```
- **`ai_enabled`**: Enables/disables AI-driven automation.
- **`default_export_format`**: Sets default format for asset exports (`fbx`, `obj`, `gltf`).
- **`logging_level`**: Controls log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **`auto_update`**: Enables automatic updates for MCP.

---

## **2. Blender-MCP Configuration**
### **2.1 Scene Generation**
```json
{
  "scene_generation": {
    "default_style": "realistic",
    "terrain_detail": "high",
    "object_variation": true
  }
}
```
- **`default_style`**: Defines the default art style (`realistic`, `cartoon`, `sci-fi`).
- **`terrain_detail`**: Controls procedural terrain quality (`low`, `medium`, `high`).
- **`object_variation`**: Enables slight randomization for object uniqueness.

### **2.2 Asset Processing**
```json
{
  "asset_processing": {
    "texture_resolution": "4K",
    "lod_levels": 3,
    "batch_processing": true
  }
}
```
- **`texture_resolution`**: Sets texture quality (`1K`, `2K`, `4K`, `8K`).
- **`lod_levels`**: Defines the number of Levels of Detail (LODs) for optimizations.
- **`batch_processing`**: Enables bulk asset processing.

---

## **3. Unreal Engine 5-MCP Configuration**
### **3.1 Level Design Automation**
```json
{
  "level_design": {
    "default_terrain_size": [1000, 1000],
    "auto_populate": true,
    "npc_spawn_density": 0.5
  }
}
```
- **`default_terrain_size`**: Defines the default width and height for terrain.
- **`auto_populate`**: Automates asset placement in levels.
- **`npc_spawn_density`**: Controls the density of AI-generated NPCs (0.0 - 1.0).

### **3.2 Performance Optimization**
```json
{
  "performance": {
    "dynamic_lighting": false,
    "max_polycount": 500000,
    "physics_enabled": true
  }
}
```
- **`dynamic_lighting`**: Enables real-time lighting effects.
- **`max_polycount`**: Defines the polygon limit per object.
- **`physics_enabled`**: Toggles physics simulation for assets.

---

## **4. AI Integration**
```json
{
  "ai_integration": {
    "provider": "openai",
    "api_key": "your-api-key",
    "ai_suggestions": true
  }
}
```
- **`provider`**: Specifies the AI service (`openai`, `stable_diffusion`).
- **`api_key`**: API key for AI integration.
- **`ai_suggestions`**: Enables AI-generated recommendations.

---

## **5. Updating Configurations**
To update settings, edit `mcp_config.json` or use:
```bash
mcp.config set key value
```
Example:
```bash
mcp.config set logging_level DEBUG
```

For troubleshooting issues, see `troubleshooting.md`.

