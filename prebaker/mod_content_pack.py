# prebaker/mod_content_pack.py

import os
import xml.etree.ElementTree as ET
from .logs import Log_Error
from .patch_operations import parsePatchOperation

class LoadableXmlAsset:
    def __init__(self, xmlDoc, fullFolderPath, name, mod):
        self.xmlDoc = xmlDoc
        self.fullFolderPath = fullFolderPath
        self.name = name
        self.mod = mod

class ModContentPack:
    def __init__(self, rootDir, packageId, packageIdPlayerFacing, loadIndex, name, official):
        self.RootDir = rootDir
        self.PackageId = packageId
        self.PackageIdPlayerFacing = packageIdPlayerFacing
        self.Name = name
        self.Official = official
        self.loadIndex = loadIndex
        self.loadedAssets = []
        self.patches = []

    def __str__(self):
        return f"{self.Name}({self.PackageId})"

    @property
    def Patches(self):
        return self.patches

    def ReloadContent(self, hotReload=False):
        pass

    def AnyContentLoaded(self):
        return bool(self.loadedAssets or self.patches)

    def LoadDefs(self, hotReload=False):
        results = []
        defsDir = os.path.join(self.RootDir, "Defs")
        if os.path.isdir(defsDir):
            for root, dirs, files in os.walk(defsDir):
                for file in files:
                    if file.lower().endswith(".xml"):
                        fpath = os.path.join(root, file)
                        try:
                            doc = ET.parse(fpath)
                            asset = LoadableXmlAsset(doc, fpath, file, self)
                            results.append(asset)
                        except Exception as ex:
                            Log_Error(f"Failed to parse XML at {fpath}: {ex}")

        # Load patch operations from /Patches
        patchDir = os.path.join(self.RootDir, "Patches")
        if os.path.isdir(patchDir):
            for root, dirs, files in os.walk(patchDir):
                for file in files:
                    if file.lower().endswith(".xml"):
                        fpath = os.path.join(root, file)
                        try:
                            doc = ET.parse(fpath)
                            r = doc.getroot()
                            if r.tag == "Patches":
                                for child in list(r):
                                    op = parsePatchOperation(child)
                                    if op:
                                        self.patches.append(op)
                        except Exception as ex:
                            Log_Error(f"Failed to parse patch XML at {fpath}: {ex}")

        self.loadedAssets = results
        return results

    def ClearDefs(self):
        self.loadedAssets.clear()

    def ClearPatchesCache(self):
        self.patches.clear()

    def ClearDestroy(self):
        pass

    def AddDef(self, defObj, assetName):
        # Real RimWorld tracks the def's origin. We do nothing.
        pass

