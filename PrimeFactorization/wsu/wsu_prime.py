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
    input_file_path = "wsu.xml"
    output_file_path = "prime_wsu.xml"
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

    # Create the XML structure
    new_element = Element("newCourse")

    new_element.append(Element("footnote"))
    new_element[-1].text = "NEW"

    new_element.append(Element("sln"))
    new_element[-1].text = "99999"

    new_element.append(Element("prefix"))
    new_element[-1].text = "CS"

    new_element.append(Element("crs"))
    new_element[-1].text = "505"

    new_element.append(Element("lab"))  # empty element

    new_element.append(Element("sect"))
    new_element[-1].text = "01"

    new_element.append(Element("title"))
    new_element[-1].text = "ADV ALGORITHMS"

    new_element.append(Element("credit"))
    new_element[-1].text = "4.0"

    new_element.append(Element("days"))
    new_element[-1].text = "M,W"

    # Nested times
    times = Element("times")
    start = Element("start")
    start.text = "14:00"
    end = Element("end")
    end.text = "15:30"
    times.append(start)
    times.append(end)
    new_element.append(times)

    # Nested place
    place = Element("place")
    bldg = Element("bldg")
    bldg.text = "ENGR"
    room = Element("room")
    room.text = "101"
    place.append(bldg)
    place.append(room)
    new_element.append(place)

    new_element.append(Element("instructor"))
    new_element[-1].text = "DR. SMITH"

    new_element.append(Element("limit"))
    new_element[-1].text = "60"

    new_element.append(Element("enrolled"))
    new_element[-1].text = "0"
    
    # Insert the new node
    new_node = XmlLabeler.BuildTree(new_element)
    

    # Relabel the tree after insertion
    start_time = time.time()
    initial_memory = XmlLabeler.GetMemoryUsage()

    prime_labeler.InsertLabeledNode(root_node, new_node)

    final_memory = XmlLabeler.GetMemoryUsage()
    elapsed_time = (time.time() - start_time) * 1000  # ms

    print(f"Time taken to label after insertion: {elapsed_time:.2f} ms")
    print(f"Memory Used During Relabeling After Insertion: {final_memory - initial_memory} KB")

    # Export the labeled XML
    XmlLabeler.ExportLabeledXml(root_node, output_file_path)
    print(f"Labeled XML has been saved to {output_file_path}")

if __name__ == "__main__":
    main()