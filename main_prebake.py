# main_prebake.py

import os
import shutil
import xml.etree.ElementTree as ET

from prebaker.loaded_mod_manager import LoadedModManager
from prebaker.def_database import GenDefDatabase
from prebaker.logs import Log_Message
from prebaker.utils import copy_assemblies_to_mega_mod

def main_prebake():
    # 1) Clear previous DB
    GenDefDatabase.ClearAll()
    LoadedModManager.runningMods.clear()
    LoadedModManager.runningModClasses.clear()
    LoadedModManager.patchedDefs.clear()

    # 2) Load all active mods => merges XML, applies patches, resolves inheritance
    LoadedModManager.LoadAllActiveMods(hotReload=False)

    # 3) Make a final folder
    outDir = "MyMergedMod"
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.makedirs(outDir, exist_ok=True)
    os.makedirs(os.path.join(outDir, "Defs"), exist_ok=True)
    os.makedirs(os.path.join(outDir, "About"), exist_ok=True)

    # 4) Copy all mod DLLs
    copy_assemblies_to_mega_mod(LoadedModManager.runningMods, outDir)

    # 5) Gather final defs from database
    all_defs = []
    for defTypeName, defMap in GenDefDatabase._defs.items():
        for defName, defObj in defMap.items():
            all_defs.append(defObj)

    # 6) Write each Def to .xml
    for d in all_defs:
        root = ET.Element("Defs")
        el = ET.SubElement(root, "MergedDef")
        dn = ET.SubElement(el, "defName")
        dn.text = d.defName
        filename = f"{d.defName}.xml"
        path = os.path.join(outDir, "Defs", filename)
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    # 7) Minimal About.xml
    about_content = """<?xml version="1.0" encoding="utf-8"?>
<ModMetaData>
    <name>MyMergedMod</name>
    <packageId>com.example.mymergedmod</packageId>
    <description>Pre-baked mod: merged XML + copied DLLs</description>
    <author>You</author>
</ModMetaData>
"""
    with open(os.path.join(outDir, "About", "About.xml"), "w", encoding="utf-8") as f:
        f.write(about_content)

    Log_Message("Pre-baking complete! Check 'MyMergedMod' folder.")

if __name__ == "__main__":
    main_prebake()

