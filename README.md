# [WIP] Prebake RimWorld Mods

This is a WIP Python-based tool that **pre-bakes** your RimWorld mods by merging all their XML Defs and copying their DLL files into a single “mega-mod.” The primary goals are to:

1. **Reduce the amount of XML merging** that RimWorld performs at startup (cutting down on load times caused by thousands of Defs).  
2. **Collect all mod assemblies** (`.dll` files) into one place (so you can enable just this one mod instead of dozens).

> **Note**: This approach does **not** remove or unify the Harmony patch overhead in those DLLs. RimWorld will still run each mod’s Harmony patches at startup. However, you should see improved load times for large modlists that contain many XML Defs.

---

## Features

- **XML Def Pre-Baking**  
  Reads and merges XML definitions from all your mods, applying inheritance (`<parentName>`) and patch operations (`PatchOperationAdd`, `PatchOperationRemove`, etc.) before creating a **single** set of final `.xml` files.

- **Assembly Copying**  
  Collects each mod’s `.dll` files from `Assemblies/` folders and copies them into your merged mod’s `Assemblies/`. This ensures all the mod code remains functional (i.e., Harmony patches, custom logic).

- **Minimal Setup**  
  - Write your mod list in a single place (`config.py`), then run the script.  
  - No advanced environment needed beyond Python 3.x.

- **Modular Codebase**  
  Each major portion of logic (logging, patching, inheritance, loaded mod manager, etc.) is split into distinct Python modules.

---
