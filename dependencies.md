# MCP Dependencies

## Overview
This document outlines the required dependencies for running Model Context Protocol (MCP) with Blender and Unreal Engine 5 (UE5). These dependencies include Python packages, Blender add-ons, and UE5 integrations.

---

## **1. General Dependencies**
### **1.1 Python Requirements**
MCP requires Python 3.x. The following Python packages must be installed:

#### Required Packages:
```bash
pip install numpy scipy pillow requests openai unrealcv
```
- `numpy`: Used for mathematical computations and optimizations.
- `scipy`: Required for advanced mathematical operations in procedural generation.
- `pillow`: Used for image and texture processing.
- `requests`: Handles API communication.
- `openai`: Required for AI-based automation features.
- `unrealcv`: Enables MCP communication with Unreal Engine.

---

## **2. Blender-Specific Dependencies**
### **2.1 Blender Version**
- Blender 3.x or later is required for MCP.

### **2.2 Required Blender Add-ons**
- **Node Wrangler**: Enhances material creation workflows.
- **Blender Python API**: Required for automation scripting.

To enable the required add-ons:
1. Open Blender
2. Navigate to `Edit` → `Preferences` → `Add-ons`
3. Search for `Node Wrangler` and enable it.

---

## **3. Unreal Engine 5-Specific Dependencies**
### **3.1 UE5 Version**
- Unreal Engine 5.1 or later is required.

### **3.2 Required Plugins**
- **Python Editor Script Plugin**: Enables Python scripting within UE5.
- **UnrealCV Plugin**: Facilitates AI-driven automation.
- **Procedural Content Generation (PCG) Framework**: Used for automated level generation.

### **3.3 Installing Plugins in UE5**
1. Open Unreal Engine 5
2. Navigate to `Edit` → `Plugins`
3. Search for and enable:
   - `Python Editor Script Plugin`
   - `UnrealCV Plugin`
   - `Procedural Content Generation (PCG) Framework`
4. Restart UE5 for changes to take effect.

---

## **4. Additional Requirements**
### **4.1 AI Integration Dependencies**
If using AI-powered automation, you need:
- **OpenAI API Key** (for AI-driven commands and procedural generation)
- **Stable Diffusion or Similar Models** (for AI-generated textures and materials)

### **4.2 Hardware Requirements**
- **Blender & UE5**: Requires a system with at least 16GB RAM and a GPU with dedicated VRAM (NVIDIA RTX 30 series or higher recommended).
- **AI Processing**: Some AI-based features may require additional GPU resources or cloud-based computing.

For configuration details, refer to `configurations.md`.

