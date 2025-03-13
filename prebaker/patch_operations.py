# prebaker/patch_operations.py

import copy
import xml.etree.ElementTree as ET
from .logs import Log_Error

def _selectNodes(xmlDoc, xpath):
    # Very naive "split on /" approach
    parts = [p for p in xpath.split('/') if p]
    current = [xmlDoc.getroot()]
    for part in parts:
        new_current = []
        for node in current:
            new_current.extend([child for child in node if child.tag == part])
        current = new_current
    return current

def _removeNode(root, target):
    for child in list(root):
        if child is target:
            root.remove(child)
            return True
        if _removeNode(child, target):
            return True
    return False

def _findParent(root, target):
    for child in list(root):
        if child is target:
            return root
        p = _findParent(child, target)
        if p is not None:
            return p
    return None

# Base patch op
class PatchOperation:
    def Apply(self, xmlDoc):
        raise NotImplementedError

    def ConfigErrors(self):
        return []

    def Complete(self, modName):
        pass

# Concrete patch ops
class PatchOperationAdd(PatchOperation):
    def __init__(self, xpath, valueNode):
        self.xpath = xpath
        self.valueNode = valueNode

    def Apply(self, xmlDoc):
        targets = _selectNodes(xmlDoc, self.xpath)
        for t in targets:
            t.append(copy.deepcopy(self.valueNode))

class PatchOperationRemove(PatchOperation):
    def __init__(self, xpath):
        self.xpath = xpath

    def Apply(self, xmlDoc):
        targets = _selectNodes(xmlDoc, self.xpath)
        for t in targets:
            _removeNode(xmlDoc.getroot(), t)

class PatchOperationReplace(PatchOperation):
    def __init__(self, xpath, valueNode):
        self.xpath = xpath
        self.valueNode = valueNode

    def Apply(self, xmlDoc):
        targets = _selectNodes(xmlDoc, self.xpath)
        for t in targets:
            parent = _findParent(xmlDoc.getroot(), t)
            if parent is not None:
                idx = list(parent).index(t)
                parent.remove(t)
                parent.insert(idx, copy.deepcopy(self.valueNode))

class PatchOperationSequence(PatchOperation):
    def __init__(self, ops):
        self.ops = ops

    def Apply(self, xmlDoc):
        for op in self.ops:
            op.Apply(xmlDoc)

def parsePatchOperation(el):
    tag = el.tag
    if tag == "PatchOperationAdd":
        xp = el.find("xpath")
        val = el.find("value")
        if xp is None or val is None:
            Log_Error("PatchOperationAdd missing <xpath> or <value>")
            return None
        if len(val) == 0:
            Log_Error("PatchOperationAdd <value> has no children.")
            return None
        return PatchOperationAdd(xp.text.strip(), val[0])
    elif tag == "PatchOperationRemove":
        xp = el.find("xpath")
        if xp is None:
            Log_Error("PatchOperationRemove missing <xpath>")
            return None
        return PatchOperationRemove(xp.text.strip())
    elif tag == "PatchOperationReplace":
        xp = el.find("xpath")
        val = el.find("value")
        if xp is None or val is None:
            Log_Error("PatchOperationReplace missing <xpath> or <value>")
            return None
        if len(val) == 0:
            Log_Error("PatchOperationReplace <value> has no child.")
            return None
        return PatchOperationReplace(xp.text.strip(), val[0])
    elif tag == "PatchOperationSequence":
        subops = []
        for child in list(el):
            op = parsePatchOperation(child)
            if op:
                subops.append(op)
        return PatchOperationSequence(subops)
    else:
        Log_Error(f"Unknown patch operation type: {tag}")
        return None

