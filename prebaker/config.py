# prebaker/config.py

from .logs import Log_Warning

class ModMetaData:
    def __init__(self, name, packageId, rootDir, official=False):
        self.Name = name
        self.PackageId = packageId
        self.RootDir = rootDir
        self.Official = official

    def __str__(self):
        return f"{self.Name}({self.PackageId}) @ {self.RootDir}"

class ModsConfig:
    """
    Example config. In real usage, parse user config or load from a file.
    """
    ActiveModsInLoadOrder = [
        ModMetaData("Core", "ludeon.rimworld.core", "Mods/Core", official=True),
        ModMetaData("ExampleMod1", "author.examplemod1", "Mods/ExampleMod1"),
        ModMetaData("ExampleMod2", "author.examplemod2", "Mods/ExampleMod2"),
    ]

    @staticmethod
    def SetActive(packageId, active):
        Log_Warning(f"SetActive called for {packageId} -> {active} (no-op in script).")

    @staticmethod
    def AreAllActive(packageIdLower):
        for mm in ModsConfig.ActiveModsInLoadOrder:
            if mm.PackageId.lower() == packageIdLower:
                return True
        return False

    @staticmethod
    def IsAnyActiveOrEmpty(packageIds):
        for pid in packageIds:
            if ModsConfig.AreAllActive(pid):
                return True
        return False

