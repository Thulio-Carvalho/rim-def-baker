# prebaker/def_database.py

from collections import defaultdict

class Def:
    def __init__(self):
        self.defName = ""
        self.modContentPack = None

    def ClearCachedData(self):
        pass

class GenDefDatabase:
    _defs = defaultdict(dict)

    @staticmethod
    def ClearAll():
        GenDefDatabase._defs.clear()

    @staticmethod
    def AddDef(defObj):
        tName = type(defObj).__name__
        GenDefDatabase._defs[tName][defObj.defName] = defObj

    @staticmethod
    def GetDefSilentFail(defType, defName):
        return GenDefDatabase._defs[defType.__name__].get(defName)

