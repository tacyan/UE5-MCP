# MCP Monorepo Structure

## Overview
This document defines the structure of the MCP monorepo, ensuring modularity, maintainability, and efficient collaboration across Blender-MCP and UE5-MCP components.

---

## **1. Directory Structure**
```
MCP/
│── blender_mcp/           # Blender integration module
│   │── assets/            # Prebuilt 3D assets and textures
│   │── scripts/           # Python scripts for automation
│   │── config/            # Configuration files for Blender
│   └── README.md
│
│── ue5_mcp/               # Unreal Engine 5 integration module
│   │── blueprints/        # AI-generated Blueprints
│   │── scripts/           # Python and UE5 automation scripts
│   │── config/            # Configuration files for UE5
│   └── README.md
│
│── core/                  # Shared utilities for MCP
│   │── ai/                # AI model interfaces and logic
│   │── assets/            # Common assets across Blender and UE5
│   │── utils/             # Helper functions and shared code
│   └── config.json        # Global configuration file
│
│── docs/                  # Documentation
│   │── api_reference.md   # API documentation
│   │── commands.md        # Command usage reference
│   │── configurations.md  # Configuration guide
│   │── troubleshooting.md # Troubleshooting guide
│   └── ...
│
│── tests/                 # Automated tests
│   │── blender_tests/     # Unit and integration tests for Blender-MCP
│   │── ue5_tests/         # Unit and integration tests for UE5-MCP
│   └── core_tests/        # Core MCP functionality tests
│
│── scripts/               # Utility scripts for setup and deployment
│   │── install.sh         # Installation script
│   │── update.sh          # Update script
│   └── cleanup.sh         # Cleanup script
│
│── LICENSE.md             # License details
│── README.md              # Project overview
│── requirements.txt       # Required dependencies
└── .gitignore             # Git ignore rules
```

---

## **2. Module Breakdown**
### **2.1 Blender-MCP**
- Automates Blender asset creation, texturing, and exports.
- Integrates AI-powered scene generation and asset processing.

### **2.2 UE5-MCP**
- Enhances Unreal Engine 5 with AI-assisted level design and gameplay logic automation.
- Provides tools for Blueprint generation and performance profiling.

### **2.3 Core**
- Shared libraries for AI interactions, asset handling, and performance optimizations.

### **2.4 Tests**
- Unit and integration tests to maintain MCP reliability across modules.

### **2.5 Scripts**
- Automation tools for installation, updates, and cleanup.

---

## **3. Best Practices**
- **Modular Design**: Keep modules independent but interoperable.
- **Code Reusability**: Place shared utilities in `core/` for cross-module use.
- **Documentation**: Maintain detailed docs for API, commands, and troubleshooting.
- **Version Control**: Use Git branches for feature development and releases.

For configuration settings, refer to `configurations.md`.

