# [WIP] Prebake RimWorld Mods

This is a WIP Python-based tool that **pre-bakes** your RimWorld mods by merging all their XML Defs and copying their DLL files into a single “mega-mod.” The primary goals are to:

1. **Reduce the amount of XML merging** that RimWorld performs at startup (cutting down on load times caused by thousands of Defs).  
2. **Collect all mod assemblies** (`.dll` files) into one place (so you can enable just this one mod instead of dozens).

> **Note**: This approach does **not** remove or unify the Harmony patch overhead in those DLLs. RimWorld will still run each mod’s Harmony patches at startup. However, you should see improved load times for large modlists that contain many XML Defs.

---
