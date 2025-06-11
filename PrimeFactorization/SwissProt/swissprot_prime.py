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
    def GetMemoryUsage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss // 1024  # KB
    
class PrimeLabeler:
    def label_tree(self, element, pLabel):
    # element.set("label", str(pLabel)) 
        element.Label = pLabel.copy()  
        for j in range(1, len(element.Children)+1):
            pout = pLabel.copy()
            pout.append(j)
            self.label_tree(element.Children[j-1], pout)
        
    def InsertNode(self, parent, newNode):
        parent.AddChild(newNode)

    def InsertLabeledNode(self, parent, newNode):
        parent.AddChild(newNode)
        newNode.Label = parent.Label.copy()
        newNode.Label.append(len(parent.Children))
        pLabel = newNode.Label
        for j in range(1, len(newNode.Children)+1):
            pout = pLabel.copy()
            pout.append(j)
            self.label_tree(newNode.Children[j-1], pout)

def main():
    input_file_path = "SwissProt.xml"
    output_file_path = "prime_SwissProt.xml"
    # Load XML document
    tree = ET.parse(input_file_path)
    root = tree.getroot()
    root_node = XmlLabeler.BuildTree(root)
    
    prime_labeler = PrimeLabeler()

    # Initial labeling
    start_time = time.time()
    initial_memory = XmlLabeler.GetMemoryUsage()

    prime_labeler.label_tree(root_node, [])

    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms

    print(f"Initial labeling time: {elapsed_time:.2f} ms")
    print(f"Memory Used During Labeling: {final_memory - initial_memory} KB")

    # Root Entry element with attributes
    entry = Element("Entry", {
        "id": "200K_HUMAN",
        "class": "STANDARD",
        "mtype": "PRT",
        "seqlen": "1200"
    })

    # Simple children
    ac = Element("AC")
    ac.text = "P99999"
    entry.append(ac)

    # Mod elements
    mod1 = Element("Mod", {"date": "10-JAN-2024", "Rel": "55", "type": "Created"})
    mod2 = Element("Mod", {"date": "10-JAN-2024", "Rel": "55", "type": "Last sequence update"})
    mod3 = Element("Mod", {"date": "20-FEB-2024", "Rel": "56", "type": "Last annotation update"})
    entry.extend([mod1, mod2, mod3])

    # Description and species
    descr = Element("Descr")
    descr.text = "200 KDA SIGNALING RECEPTOR PROTEIN"
    entry.append(descr)

    species = Element("Species")
    species.text = "Homo sapiens (Human)"
    entry.append(species)

    # Organism lineage
    orgs = [
        "Eukaryota", "Metazoa", "Chordata", "Craniata",
        "Vertebrata", "Mammalia", "Primates", "Hominidae", "Homo"
    ]
    for org_text in orgs:
        org = Element("Org")
        org.text = org_text
        entry.append(org)

    # Ref 1
    ref1 = Element("Ref", {"num": "1", "pos": "SEQUENCE FROM N.A"})

    comment = Element("Comment")
    comment.text = "STRAIN=REFERENCE"
    ref1.append(comment)

    db = Element("DB")
    db.text = "PUBMED"
    ref1.append(db)

    medline = Element("MedlineID")
    medline.text = "98765432"
    ref1.append(medline)

    for author_name in ["Smith J.", "Doe A.", "Brown T."]:
        author = Element("Author")
        author.text = author_name
        ref1.append(author)

    cite1 = Element("Cite")
    cite1.text = "J. Biol. Chem. 299:1234-1245(2024)"
    ref1.append(cite1)

    entry.append(ref1)

    # Ref 2
    ref2 = Element("Ref", {"num": "2", "pos": "ERRATUM"})

    author = Element("Author")
    author.text = "Smith J."
    ref2.append(author)

    cite2 = Element("Cite")
    cite2.text = "J. Biol. Chem. 300:2345-2346(2024)"
    ref2.append(cite2)

    entry.append(ref2)

    # EMBL, INTERPRO, PFAM
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
    b_descr = Element("Descr")
    b_descr.text = "GTP BINDING SITE"
    binding.append(b_descr)

    features.extend([domain1, domain2, domain3, binding])
    entry.append(features)
    new_node = XmlLabeler.BuildTree(entry)
    

    # Relabel the tree after insertion
    start_time = time.time()
    initial_memory = XmlLabeler.GetMemoryUsage()

    prime_labeler.InsertLabeledNode(root_node, new_node)

    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms

    print(f"Time taken to label after insertion: {elapsed_time:.2f} ms")
    print(f"Memory Used During Relabeling After Insertion: {final_memory - initial_memory} KB")

    # Export the labeled XML
    # XmlLabeler.ExportLabeledXml(root_node, output_file_path)
    # print(f"Labeled XML has been saved to {output_file_path}")

if __name__ == "__main__":
    main()