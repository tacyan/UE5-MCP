# MCP API Reference

## Overview
This document provides details on the APIs available in MCP for interacting with Blender and Unreal Engine 5 (UE5). These APIs facilitate AI-driven automation for asset creation, scene generation, and gameplay programming.

---

## **1. Blender-MCP API**
### **1.1 Scene Generation**
#### `generate_scene(description: str) -> Scene`
- **Description**: Creates a scene based on a natural language description.
- **Parameters**:
  - `description` (str): Text prompt describing the scene.
- **Returns**: Blender `Scene` object with generated assets.
- **Example Usage**:
  ```python
  scene = generate_scene("A dense forest with a river running through it.")
  ```

#### `add_object_to_scene(object_type: str, location: tuple) -> Object`
- **Description**: Adds a specified object to the active scene.
- **Parameters**:
  - `object_type` (str): Type of object (e.g., "tree", "rock", "building").
  - `location` (tuple): XYZ coordinates for object placement.
- **Returns**: Blender `Object` instance.
- **Example Usage**:
  ```python
  add_object_to_scene("tree", (2.5, 3.0, 0.0))
  ```

### **1.2 Asset Management**
#### `generate_texture(object: Object, texture_type: str) -> Texture`
- **Description**: Generates a procedural texture for an object.
- **Parameters**:
  - `object` (Object): Blender object to apply texture to.
  - `texture_type` (str): Type of texture (e.g., "rusted metal", "wood").
- **Returns**: Blender `Texture` object.

#### `export_asset(asset: Object, format: str, filepath: str) -> None`
- **Description**: Exports a Blender asset in a specified format.
- **Parameters**:
  - `asset` (Object): The asset to export.
  - `format` (str): File format (`.fbx`, `.obj`, `.gltf`).
  - `filepath` (str): Destination file path.

---

## **2. Unreal Engine 5-MCP API**
### **2.1 Level Design Automation**
#### `generate_terrain(size: tuple, detail_level: str) -> Terrain`
- **Description**: Creates procedural terrain based on given parameters.
- **Parameters**:
  - `size` (tuple): Width and height of terrain.
  - `detail_level` (str): "low", "medium", or "high" resolution.
- **Returns**: UE5 `Terrain` object.

#### `populate_level(asset_type: str, density: int) -> None`
- **Description**: Populates the level with specified assets.
- **Parameters**:
  - `asset_type` (str): Type of asset ("trees", "rocks", "buildings").
  - `density` (int): Number of assets to place.

### **2.2 Blueprint Automation**
#### `generate_blueprint(logic_description: str) -> Blueprint`
- **Description**: Creates a UE5 Blueprint based on a natural language description.
- **Parameters**:
  - `logic_description` (str): Description of gameplay behavior.
- **Returns**: UE5 `Blueprint` instance.
- **Example Usage**:
  ```python
  blueprint = generate_blueprint("A door that opens when the player interacts with it.")
  ```

### **2.3 Debugging & Optimization**
#### `profile_performance(level: Level) -> Report`
- **Description**: Runs a performance analysis on the current level.
- **Parameters**:
  - `level` (Level): The current game level.
- **Returns**: Performance `Report` object with optimization suggestions.

---

## **3. API Authentication & Configuration**
- **API Key**: Required for AI-based functions.
- **Configuration File**: Set in `configurations.md`.

For more details on commands and parameters, refer to `commands.md`.

