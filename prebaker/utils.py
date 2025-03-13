# prebaker/utils.py

import os
import shutil
from .logs import Log_Message

def copy_assemblies_to_mega_mod(running_mods, mega_mod_path):
    """
    Copies all .dll files from each mod's /Assemblies to `mega_mod_path/Assemblies`.
    Beware of name collisions.
    """
    asm_dir = os.path.join(mega_mod_path, "Assemblies")
    os.makedirs(asm_dir, exist_ok=True)

    for mcp in running_mods:
        src_dir = os.path.join(mcp.RootDir, "Assemblies")
        if os.path.isdir(src_dir):
            for file in os.listdir(src_dir):
                if file.lower().endswith(".dll"):
                    src = os.path.join(src_dir, file)
                    dst = os.path.join(asm_dir, file)
                    Log_Message(f"Copying DLL from {src} to {dst}")
                    shutil.copy2(src, dst)

