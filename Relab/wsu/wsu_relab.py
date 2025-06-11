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
    input_path = "wsu.xml"
    output_path = "labeled_wsu.xml"
    output_path2 = "pre_inserted_wsu.xml"
    
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
    
    # Create new node and insert it
    new_node = XmlLabeler.BuildTree(new_element)
    
    
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