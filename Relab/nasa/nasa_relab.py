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
    input_path = "nasa.xml"
    output_path = "labeled_nasa.xml"
    output_path2 = "pre_inserted_nasa.xml"
    
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

    # Export the labeled XML
    XmlLabeler.ExportLabeledXml(root_node, output_path2)
    # tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Labeled XML has been saved to {output_path2}")
    
    # Create new element to insert
    new_element = Element("dataset")
    new_element.set("subject", "astronomy")
    new_element.set("xmlns:xlink", "http://www.w3.org/XML/XLink/0.9")
    
    title = Element("title")
    title.text = "Proper Motions of Stars in the Zone Catalogue -40 to -52 degrees of 20843 Stars for 1900"
    new_element.append(title)
    
    altname1 = Element("altname")
    altname1.set("type", "ADC")
    altname1.text = "1005"
    new_element.append(altname1)
    
    altname2 = Element("altname")
    altname2.set("type", "CDS")
    altname2.text = "I/5"
    new_element.append(altname2)
    
    altname3 = Element("altname")
    altname3.set("type", "brief")
    altname3.text = "Proper Motions in Cape Zone Catalogue -40/-52"
    new_element.append(altname3)
    
    reference = Element("reference")
    source = Element("source")
    other = Element("other")
    
    other_title = Element("title")
    other_title.text = "Proper Motions of Stars in the Zone Catalogue"
    other.append(other_title)
    
    author1 = Element("author")
    initial1 = Element("initial")
    initial1.text = "J"
    lastName1 = Element("lastName")
    lastName1.text = "Spencer"
    author1.append(initial1)
    author1.append(lastName1)
    other.append(author1)
    
    author2 = Element("author")
    initial2 = Element("initial")
    initial2.text = "J"
    lastName2 = Element("lastName")
    lastName2.text = "Jackson"
    author2.append(initial2)
    author2.append(lastName2)
    other.append(author2)
    
    name = Element("name")
    name.text = "His Majesty's Stationery Office, London"
    other.append(name)
    
    publisher = Element("publisher")
    publisher.text = "???"
    other.append(publisher)
    
    city = Element("city")
    city.text = "???"
    other.append(city)
    
    date = Element("date")
    year = Element("year")
    year.text = "1936"
    date.append(year)
    other.append(date)
    
    source.append(other)
    reference.append(source)
    new_element.append(reference)
    
    keywords = Element("keywords")
    keywords.set("parentListURL", "http://messier.gsfc.nasa.gov/xml/keywordlists/adc_keywords.html")
    
    keyword1 = Element("keyword")
    keyword1.set("xlink:href", "Positional_data.html")
    keyword1.text = "Positional data"
    keywords.append(keyword1)
    
    keyword2 = Element("keyword")
    keyword2.set("xlink:href", "Proper_motions.html")
    keyword2.text = "Proper motions"
    keywords.append(keyword2)
    
    new_element.append(keywords)
    
    descriptions = Element("descriptions")
    description = Element("description")
    para = Element("para")
    para.text = "This catalog, listing the proper motions of 20,843 stars from the Cape Astrographic Zones..."
    description.append(para)
    descriptions.append(description)
    descriptions.append(Element("details"))
    new_element.append(descriptions)
    
    identifier = Element("identifier")
    identifier.text = "I_5.xml"
    new_element.append(identifier)
    
    # Create new node and insert it
    new_node = XmlNode("dataset", new_element)
    
    
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
    # tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Labeled XML has been saved to {output_path}")

if __name__ == "__main__":
    main()