# VULNERABLE
import xml.etree.ElementTree as ET
def parse_xml_vulnerable(xml_data):
    root = ET.fromstring(xml_data)
    return root

