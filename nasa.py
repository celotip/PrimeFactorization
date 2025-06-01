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

input_file_path = "nasa.xml"
output_file_path = "insert_nasa.xml"

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss // 1024  # KB

def get_xml_depth(element):
    if len(element) == 0:  # No children → depth 1
        return 1
    else:
        return 1 + max(get_xml_depth(child) for child in element)
    
def generate_primes(depth):
    """Generate an array of prime numbers up to the specified depth/count.
    Returns: [1, 2, 3, 5, 7, 11, ...] (p[0] = 1, p[1] = 2, etc.)
    """
    if depth < 1:
        return [1]  # At least return p[0] = 1
    
    primes = [1, 2]  # Initialize with p[0]=1 and p[1]=2
    if depth == 1:
        return primes[:2]  # Return [1, 2] if depth=1
    
    num = 3  # Start checking from 3
    while len(primes) <= depth:
        is_prime = True
        # Check divisibility with existing primes (skip p[0]=1)
        for p in primes[1:]:
            if p * p > num:
                break  # No need to check beyond sqrt(num)
            if num % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
        num += 2  # Skip even numbers
    
    return primes[:depth + 1] 

def label_tree(element, pLabel, p, d):
    element.set("label", str(pLabel))
    
    for child in list(element):  # Create a list to avoid modification during iteration
        child_label = pLabel * p[d]
        label_tree(child, child_label, p, d + 1)

def main():
    # Load XML document
    tree = ET.parse(input_file_path)
    root = tree.getroot()

    depth = get_xml_depth(root)
    print(f"XML tree depth: {depth}")

    p = generate_primes(depth)

    # Initial labeling
    start_time = time.time()
    initial_memory = get_memory_usage()

    label_tree(root, 1, p, 0)

    final_memory = get_memory_usage()
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
    root.append(new_element)

    # Relabel the tree after insertion
    start_time = time.time()
    initial_memory = get_memory_usage()

    label_tree(root, 1, p, 0)

    final_memory = get_memory_usage()
    elapsed_time = (time.time() - start_time) * 1000  # ms

    print(f"Time taken to label after insertion: {elapsed_time:.2f} ms")
    print(f"Memory Used During Relabeling After Insertion: {final_memory - initial_memory} KB")

    # Write the XML file
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
    print(f"Labeled XML has been saved to {output_file_path}")

if __name__ == "__main__":
    main()