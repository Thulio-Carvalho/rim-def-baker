# prebaker/loaded_mod_manager.py

import copy
import xml.etree.ElementTree as ET

from .logs import DeepProfiler, Log_Error, Log_Warning
from .config import ModsConfig
from .mod_content_pack import ModContentPack
from .xml_inheritance import XmlInheritance
from .def_database import Def, GenDefDatabase
from .patch_operations import PatchOperation
from .logs import Log_Message

class LongEventHandler:
    @staticmethod
    def ExecuteWhenFinished(action):
        action()

class TKeySystem:
    @staticmethod
    def Clear():
        pass
    @staticmethod
    def Parse(xmlDoc):
        pass

def _checkMayRequire(node):
    if node is None or node.attrib is None:
        return True
    mr = node.attrib.get("MayRequire", None)
    if mr and not ModsConfig.AreAllActive(mr.lower()):
        return False
    mrao = node.attrib.get("MayRequireAnyOf", None)
    if mrao:
        arr = [x.strip().lower() for x in mrao.split(',')]
        if not ModsConfig.IsAnyActiveOrEmpty(arr):
            return False
    return True

class DirectXmlLoader:
    @staticmethod
    def DefFromNode(xmlNode, asset):
        dn = xmlNode.find("defName")
        if dn is None or not dn.text.strip():
            return None
        d = Def()
        d.defName = dn.text.strip()
        if asset:
            d.modContentPack = asset.mod
        return d

class LoadedModManager:
    runningMods = []
    runningModClasses = {}
    patchedDefs = []

    @staticmethod
    def LoadAllActiveMods(hotReload=False):
        DeepProfiler.Start("XmlInheritance.Clear()")
        XmlInheritance.Clear()
        DeepProfiler.End()

        if not hotReload:
            DeepProfiler.Start("InitializeMods()")
            LoadedModManager.InitializeMods()
            DeepProfiler.End()

        DeepProfiler.Start("LoadModContent()")
        LoadedModManager.LoadModContent(hotReload)
        DeepProfiler.End()

        DeepProfiler.Start("CreateModClasses()")
        LoadedModManager.CreateModClasses()
        DeepProfiler.End()

        DeepProfiler.Start("LoadModXML()")
        xmls = LoadedModManager.LoadModXML(hotReload)
        DeepProfiler.End()

        assetlookup = {}
        DeepProfiler.Start("CombineIntoUnifiedXML()")
        xmlDoc = LoadedModManager.CombineIntoUnifiedXML(xmls, assetlookup)
        DeepProfiler.End()

        if not hotReload:
            TKeySystem.Clear()
            DeepProfiler.Start("TKeySystem.Parse()")
            TKeySystem.Parse(xmlDoc)
            DeepProfiler.End()

            DeepProfiler.Start("ErrorCheckPatches()")
            LoadedModManager.ErrorCheckPatches()
            DeepProfiler.End()

        DeepProfiler.Start("ApplyPatches()")
        LoadedModManager.ApplyPatches(xmlDoc, assetlookup)
        DeepProfiler.End()

        DeepProfiler.Start("ParseAndProcessXML()")
        LoadedModManager.ParseAndProcessXML(xmlDoc, assetlookup, hotReload)
        DeepProfiler.End()

        DeepProfiler.Start("ClearCachedPatches()")
        LoadedModManager.ClearCachedPatches()
        DeepProfiler.End()

        DeepProfiler.Start("XmlInheritance.Clear()")
        XmlInheritance.Clear()
        DeepProfiler.End()

    @staticmethod
    def InitializeMods():
        idx = 0
        for meta in ModsConfig.ActiveModsInLoadOrder:
            if not os.path.isdir(meta.RootDir):
                ModsConfig.SetActive(meta.PackageId, False)
                Log_Warning(f"Failed to find active mod {meta.Name} @ {meta.RootDir}")
                continue
            mcp = ModContentPack(meta.RootDir, meta.PackageId, meta.PackageId, idx, meta.Name, meta.Official)
            idx += 1
            LoadedModManager.runningMods.append(mcp)

    @staticmethod
    def LoadModContent(hotReload=False):
        LongEventHandler.ExecuteWhenFinished(lambda: DeepProfiler.Start("LoadModContent"))
        for mcp in LoadedModManager.runningMods:
            DeepProfiler.Start(f"Loading content for {mcp}")
            mcp.ReloadContent(hotReload)
            DeepProfiler.End()

        def finish():
            DeepProfiler.End()
            for mcp in LoadedModManager.runningMods:
                if not mcp.AnyContentLoaded():
                    Log_Error(f"Mod {mcp.Name} did not load any content.")
        LongEventHandler.ExecuteWhenFinished(finish)

    @staticmethod
    def CreateModClasses():
        # In real RimWorld, it scans assemblies for classes deriving from `Mod`.
        pass

    @staticmethod
    def LoadModXML(hotReload=False):
        assets = []
        for mcp in LoadedModManager.runningMods:
            DeepProfiler.Start(f"LoadModXML => {mcp}")
            newAssets = mcp.LoadDefs(hotReload)
            assets.extend(newAssets)
            DeepProfiler.End()
        return assets

    @staticmethod
    def CombineIntoUnifiedXML(xmls, assetlookup):
        root = ET.Element("Defs")
        for asset in xmls:
            docRoot = asset.xmlDoc.getroot()
            if docRoot is None:
                Log_Error(f"{asset.fullFolderPath}/{asset.name}: parse failure")
                continue
            if docRoot.tag != "Defs":
                Log_Error(f"{asset.fullFolderPath}/{asset.name}: root is {docRoot.tag}, expected 'Defs'")
            for child in list(docRoot):
                c = copy.deepcopy(child)
                assetlookup[c] = asset
                root.append(c)
        return ET.ElementTree(root)

    @staticmethod
    def ErrorCheckPatches():
        for mcp in LoadedModManager.runningMods:
            for patch in mcp.Patches:
                for err in patch.ConfigErrors():
                    Log_Error(f"Patch error in {mcp.Name}: {err}")

    @staticmethod
    def ApplyPatches(xmlDoc, assetlookup):
        for mcp in LoadedModManager.runningMods:
            for patch in mcp.Patches:
                patch.Apply(xmlDoc)

    @staticmethod
    def ParseAndProcessXML(xmlDoc, assetlookup, hotReload=False):
        root = xmlDoc.getroot()
        allNodes = list(root)
        for node in allNodes:
            XmlInheritance.TryRegister(node, assetlookup.get(node).mod if node in assetlookup else None)

        XmlInheritance.Resolve()

        if hotReload:
            for mcp in LoadedModManager.runningMods:
                mcp.ClearDefs()
        LoadedModManager.patchedDefs.clear()

        for node in XmlInheritance.registry:
            if not _checkMayRequire(node):
                continue
            asset = assetlookup.get(node)
            d = DirectXmlLoader.DefFromNode(node, asset)
            if d:
                if asset and asset.mod:
                    asset.mod.AddDef(d, asset.name)
                else:
                    LoadedModManager.patchedDefs.append(d)
                GenDefDatabase.AddDef(d)

    @staticmethod
    def ClearCachedPatches():
        for mcp in LoadedModManager.runningMods:
            for patch in mcp.Patches:
                patch.Complete(mcp.Name)
            mcp.ClearPatchesCache()

    @staticmethod
    def ClearDestroy():
        for mcp in LoadedModManager.runningMods:
            mcp.ClearDestroy()
        LoadedModManager.runningMods.clear()

