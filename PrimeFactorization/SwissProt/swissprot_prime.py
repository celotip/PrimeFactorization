import xml.etree.ElementTree as ET
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
    def label_tree(self, element, pLabel, d):
    # element.set("label", str(pLabel)) 
        element.Label = pLabel.copy()  
        for j in range(1, len(element.Children)+1):
            pout = pLabel.copy()
            pout.append(j)
            self.label_tree(element.Children[j-1], pout, d + 1)
        
    def InsertNode(self, parent, newNode):
        parent.AddChild(newNode)

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

    prime_labeler.label_tree(root_node, [], 0)

    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms

    print(f"Initial labeling time: {elapsed_time:.2f} ms")
    print(f"Memory Used During Labeling: {final_memory - initial_memory} KB")

    # Create new element to insert
    new_element = ET.Element("dataset")
    new_element.set("subject", "astronomy")
    new_element.set("xmlns:xlink", "http://www.w3.org/XML/XLink/0.9")
    
    title = ET.SubElement(new_element, "title")
    title.text = "Proper Motions of Stars in the Zone Catalogue -40 to -52 degrees of 20843 Stars for 1900"
    
    altname1 = ET.SubElement(new_element, "altname")
    altname1.set("type", "ADC")
    altname1.text = "1005"
    
    altname2 = ET.SubElement(new_element, "altname")
    altname2.set("type", "CDS")
    altname2.text = "I/5"
    
    altname3 = ET.SubElement(new_element, "altname")
    altname3.set("type", "brief")
    altname3.text = "Proper Motions in Cape Zone Catalogue -40/-52"
    
    reference = ET.SubElement(new_element, "reference")
    source = ET.SubElement(reference, "source")
    other = ET.SubElement(source, "other")
    
    other_title = ET.SubElement(other, "title")
    other_title.text = "Proper Motions of Stars in the Zone Catalogue"
    
    author1 = ET.SubElement(other, "author")
    initial1 = ET.SubElement(author1, "initial")
    initial1.text = "J"
    lastName1 = ET.SubElement(author1, "lastName")
    lastName1.text = "Spencer"
    
    author2 = ET.SubElement(other, "author")
    initial2 = ET.SubElement(author2, "initial")
    initial2.text = "J"
    lastName2 = ET.SubElement(author2, "lastName")
    lastName2.text = "Jackson"
    
    name = ET.SubElement(other, "name")
    name.text = "His Majesty's Stationery Office, London"
    
    publisher = ET.SubElement(other, "publisher")
    publisher.text = "???"
    
    city = ET.SubElement(other, "city")
    city.text = "???"
    
    date = ET.SubElement(other, "date")
    year = ET.SubElement(date, "year")
    year.text = "1936"
    
    keywords = ET.SubElement(new_element, "keywords")
    keywords.set("parentListURL", "http://messier.gsfc.nasa.gov/xml/keywordlists/adc_keywords.html")
    
    keyword1 = ET.SubElement(keywords, "keyword")
    keyword1.set("xlink:href", "Positional_data.html")
    keyword1.text = "Positional data"
    
    keyword2 = ET.SubElement(keywords, "keyword")
    keyword2.set("xlink:href", "Proper_motions.html")
    keyword2.text = "Proper motions"
    
    descriptions = ET.SubElement(new_element, "descriptions")
    description = ET.SubElement(descriptions, "description")
    para = ET.SubElement(description, "para")
    para.text = "This catalog, listing the proper motions of 20,843 stars from the Cape Astrographic Zones..."
    ET.SubElement(descriptions, "details")
    
    identifier = ET.SubElement(new_element, "identifier")
    identifier.text = "I_5.xml"
    
    # Insert the new node
    new_node = XmlNode("dataset", new_element)
    prime_labeler.InsertNode(root_node, new_node)

    # Relabel the tree after insertion
    start_time = time.time()
    initial_memory = XmlLabeler.GetMemoryUsage()

    prime_labeler.label_tree(root_node, [], 0)

    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms

    print(f"Time taken to label after insertion: {elapsed_time:.2f} ms")
    print(f"Memory Used During Relabeling After Insertion: {final_memory - initial_memory} KB")

    # Write the XML file
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
    print(f"Labeled XML has been saved to {output_file_path}")

if __name__ == "__main__":
    main()