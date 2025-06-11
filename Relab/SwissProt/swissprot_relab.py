import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import time
import os
import psutil


class XmlNode:
    def __init__(self, name, element):
        self.Name = name
        self.Children = []
        self.Label = None
        self.Element = element
    
    def AddChild(self, child):
        self.Children.append(child)

class ReLabLabel:
    def __init__(self, level, ordinal, rid):
        self.Level = level
        self.Ordinal = ordinal
        self.RID = rid
    
    def __str__(self):
        return f"[{self.Level},{self.Ordinal},{self.RID}]"

class ReLab:
    def __init__(self):
        self.currentOrdinal = 0
    
    def LabelTree(self, root):
        self.currentOrdinal = 0  # Reset ordinal counter
        self.AssignLabels(root, 0)
    
    def AssignLabels(self, node, level):
        self.currentOrdinal += 1
        node.Label = ReLabLabel(level, self.currentOrdinal, 0)

        for child in node.Children:
            self.AssignLabels(child, level + 1)
        
        if len(node.Children) > 0:
            rID = node.Children[-1].Label.Ordinal
            self.SetRID(node, rID)
    
    def SetRID(self, node, rID):
        node.Label.RID = rID
        for child in node.Children:
            self.SetRID(child, rID)
    
    def InsertNode(self, parent, newNode):
        parent.AddChild(newNode)
        # self.LabelTree(parent)  # Relabel the tree after insertion

class XmlLabeler:
    @staticmethod
    def BuildTree(element):
        node = XmlNode(element.tag, element)
        
        for child_element in element:
            child_node = XmlLabeler.BuildTree(child_element)
            node.AddChild(child_node)
        
        return node
    
    @staticmethod
    def ExportLabeledXml(node, output_path):
        labeled_element = XmlLabeler.AddLabelsToXml(node)
        tree = ET.ElementTree(labeled_element)
        # Pretty-print (Python 3.9+)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    @staticmethod
    def AddLabelsToXml(node):
        element = Element(node.Element.tag)
        element.set("label", str(node.Label))
        
        # Copy attributes from original element
        for key, value in node.Element.attrib.items():
            element.set(key, value)
        
        # Copy text content if exists
        if node.Element.text and node.Element.text.strip():
            element.text = node.Element.text
        
        # Add children
        for child in node.Children:
            element.append(XmlLabeler.AddLabelsToXml(child))
        
        return element
    
    @staticmethod
    def QueryNodes(root, path):
        path_parts = path.split('/')
        return XmlLabeler.QueryNodesRecursive(root, path_parts, 0)
    
    @staticmethod
    def QueryNodesRecursive(current, path_parts, level):
        result = []
        
        if level >= len(path_parts):
            return result
        
        current_path_part = path_parts[level]
        
        if current.Name == current_path_part or current_path_part == "*":
            if level == len(path_parts) - 1:
                result.append(current)
            else:
                for child in current.Children:
                    result.extend(XmlLabeler.QueryNodesRecursive(child, path_parts, level + 1))
        
        return result
    
    @staticmethod
    def GetMemoryUsage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss // 1024  # KB

def main():
    input_path = "SwissProt.xml"
    output_path = "labeled_SwissProt.xml"
    
    tree = ET.parse(input_path)
    root_element = tree.getroot()
    root_node = XmlLabeler.BuildTree(root_element)
    
    relab = ReLab()
    
    # Initial labeling
    start_time = time.time()
    initial_memory = XmlLabeler.GetMemoryUsage()
    
    relab.LabelTree(root_node)
    
    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms
    
    print(f"Initial labeling time: {elapsed_time:.2f} ms")
    print(f"Memory Used During Labeling: {final_memory - initial_memory} KB")
    
    # Create the Entry element with attributes
    entry = Element("Entry", {
        "id": "200K_HUMAN",
        "class": "STANDARD",
        "mtype": "PRT",
        "seqlen": "1200"
    })

    # Add simple children
    entry.append(Element("AC"))
    entry[-1].text = "P99999"

    # Add Mod elements
    mod1 = Element("Mod", {"date": "10-JAN-2024", "Rel": "55", "type": "Created"})
    mod2 = Element("Mod", {"date": "10-JAN-2024", "Rel": "55", "type": "Last sequence update"})
    mod3 = Element("Mod", {"date": "20-FEB-2024", "Rel": "56", "type": "Last annotation update"})
    entry.extend([mod1, mod2, mod3])

    # Add descriptive elements
    descr = Element("Descr")
    descr.text = "200 KDA SIGNALING RECEPTOR PROTEIN"
    species = Element("Species")
    species.text = "Homo sapiens (Human)"
    entry.extend([descr, species])

    # Organism lineage
    orgs = [
        "Eukaryota", "Metazoa", "Chordata", "Craniata",
        "Vertebrata", "Mammalia", "Primates", "Hominidae", "Homo"
    ]
    for org in orgs:
        el = Element("Org")
        el.text = org
        entry.append(el)

    # Reference 1
    ref1 = Element("Ref", {"num": "1", "pos": "SEQUENCE FROM N.A"})
    ref1.append(Element("Comment", text := "STRAIN=REFERENCE"))
    ref1.append(Element("DB", text := "PUBMED"))
    ref1.append(Element("MedlineID", text := "98765432"))
    for author in ["Smith J.", "Doe A.", "Brown T."]:
        a = Element("Author")
        a.text = author
        ref1.append(a)
    cite1 = Element("Cite")
    cite1.text = "J. Biol. Chem. 299:1234-1245(2024)"
    ref1.append(cite1)
    entry.append(ref1)

    # Reference 2
    ref2 = Element("Ref", {"num": "2", "pos": "ERRATUM"})
    a = Element("Author")
    a.text = "Smith J."
    ref2.append(a)
    cite2 = Element("Cite")
    cite2.text = "J. Biol. Chem. 300:2345-2346(2024)"
    ref2.append(cite2)
    entry.append(ref2)

    # Database cross-references
    entry.append(Element("EMBL", {"prim_id": "X12345", "sec_id": "CAA12345"}))
    entry.append(Element("INTERPRO", {"prim_id": "IPR001234", "sec_id": "-"}))
    entry.append(Element("INTERPRO", {"prim_id": "IPR005678", "sec_id": "-"}))
    entry.append(Element("PFAM", {"prim_id": "PF00123", "sec_id": "SIGNAL", "status": "1"}))
    entry.append(Element("PFAM", {"prim_id": "PF00456", "sec_id": "DOMAIN", "status": "1"}))

    # Keywords
    for kw in ["Signaling", "Receptor", "Transmembrane"]:
        keyword = Element("Keyword")
        keyword.text = kw
        entry.append(keyword)

    # Features section
    features = Element("Features")

    domain1 = Element("DOMAIN", {"from": "60", "to": "120"})
    d1_descr = Element("Descr")
    d1_descr.text = "TRANSMEMBRANE DOMAIN"
    domain1.append(d1_descr)

    domain2 = Element("DOMAIN", {"from": "300", "to": "450"})
    d2_descr = Element("Descr")
    d2_descr.text = "SIGNAL TRANSDUCTION DOMAIN"
    domain2.append(d2_descr)

    domain3 = Element("DOMAIN", {"from": "700", "to": "900"})
    d3_descr = Element("Descr")
    d3_descr.text = "ATP BINDING DOMAIN"
    domain3.append(d3_descr)

    binding = Element("BINDING", {"from": "850", "to": "860"})
    binding_descr = Element("Descr")
    binding_descr.text = "GTP BINDING SITE"
    binding.append(binding_descr)

    features.extend([domain1, domain2, domain3, binding])
    entry.append(features)
    new_node = XmlLabeler.BuildTree(entry)
    
    # Relabel the tree
    start_time = time.time()
    initial_memory = XmlLabeler.GetMemoryUsage()
    
    relab.InsertNode(root_node, new_node)
    relab.LabelTree(root_node)
    
    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms
    
    print(f"Time taken to label new insert node: {elapsed_time:.2f} ms")
    print(f"Memory Used During Relabeling After Insertion: {final_memory - initial_memory} KB")
    
    # Export the labeled XML
    XmlLabeler.ExportLabeledXml(root_node, output_path)
    print(f"Labeled XML has been saved to {output_path}")

if __name__ == "__main__":
    main()