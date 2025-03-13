# prebaker/xml_inheritance.py

import copy
import xml.etree.ElementTree as ET
from collections import defaultdict

def _isListNode(el: ET.Element) -> bool:
    for c in el:
        if c.tag == "li":
            return True
    return False

def _mergeListNode(childList, parentList):
    child_items = [ET.tostring(li, encoding='utf-8') for li in childList.findall("li")]
    for pli in parentList.findall("li"):
        pli_str = ET.tostring(pli, encoding='utf-8')
        if pli_str not in child_items:
            childList.append(copy.deepcopy(pli))

def _mergeElementsRimWorldStyle(childElem, parentElem):
    if (not childElem.text or not childElem.text.strip()) and (parentElem.text and parentElem.text.strip()):
        childElem.text = parentElem.text

    child_map = defaultdict(list)
    for c in childElem:
        child_map[c.tag].append(c)

    for p in parentElem:
        if not child_map[p.tag]:
            childElem.append(copy.deepcopy(p))
        else:
            # merge or override
            csub = child_map[p.tag][0]
            if _isListNode(p) and _isListNode(csub):
                _mergeListNode(csub, p)
            else:
                _mergeElementsRimWorldStyle(csub, p)

class XmlInheritance:
    """
    Emulates RimWorld's XML inheritance:
    - <parentName>, <abstract>, merging <li> items, etc.
    """
    registry = []

    @staticmethod
    def Clear():
        XmlInheritance.registry.clear()

    @staticmethod
    def TryRegister(node, modContentPack):
        XmlInheritance.registry.append(node)

    @staticmethod
    def Resolve():
        key_map = {}
        abstract_keys = set()

        for node in XmlInheritance.registry:
            dn = node.find("defName")
            if dn is None or not dn.text.strip():
                continue
            defName = dn.text.strip()
            key = (node.tag, defName)
            key_map[key] = node
            ab = node.find("abstract")
            if ab is not None and ab.text and ab.text.strip().lower() == "true":
                abstract_keys.add(key)

        # Repeatedly merge parent -> child
        changed = True
        while changed:
            changed = False
            for k, child in list(key_map.items()):
                parentNameNode = child.find("parentName")
                if parentNameNode is not None and parentNameNode.text:
                    parentKey = (child.tag, parentNameNode.text.strip())
                    if parentKey in key_map:
                        parent = key_map[parentKey]
                        _mergeElementsRimWorldStyle(child, parent)
                        child.remove(parentNameNode)
                        changed = True

        # remove abstracts
        final = []
        for k, node in key_map.items():
            if k not in abstract_keys:
                final.append(node)

        XmlInheritance.registry = final

