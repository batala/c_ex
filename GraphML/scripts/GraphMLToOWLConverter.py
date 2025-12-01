import xml.etree.ElementTree as ET
from datetime import datetime

class GraphMLToOWLConverter:
    def __init__(self):
        self.namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#'
        }

    def register_namespaces(self, root):
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)
            root.set(f'xmlns:{prefix}', uri)

    def convert(self, graphml_file, owl_file):
        # Parse GraphML
        tree = ET.parse(graphml_file)
        root = tree.getroot()

        # Create OWL structure
        owl_root = ET.Element('rdf:RDF')
        self.register_namespaces(owl_root)

        # Create Ontology
        ontology = ET.SubElement(owl_root, 'owl:Ontology')
        ontology.set('rdf:about', '')

        # Add ontology metadata
        title = ET.SubElement(ontology, 'rdfs:label')
        title.text = 'Converted from yFiles GraphML'
        title.set('xml:lang', 'en')

        created = ET.SubElement(ontology, 'owl:versionInfo')
        created.text = f'Created {datetime.now().isoformat()}'

        # Process nodes and edges
        graph = root.find('.//{http://graphml.graphdrawing.org/xmlns}graph')
        if graph is not None:
            self.process_graph(graph, owl_root)

        # Write OWL file
        tree = ET.ElementTree(owl_root)
        with open(owl_file, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

    def process_graph(self, graph, owl_root):
        node_classes = {}
        object_properties = {}

        # First pass: create classes from nodes
        for node in graph.findall('.//{http://graphml.graphdrawing.org/xmlns}node'):
            node_id = node.get('id')
            labels = node.findall('.//{http://www.yworks.com/xml/yfiles-common/2.0}Label')

            class_name = f"Class_{node_id}"
            if labels:
                label_text = labels[0].get('Text', class_name)
                class_name = self.sanitize_name(label_text) or class_name

            # Create OWL Class
            owl_class = ET.SubElement(owl_root, 'owl:Class')
            owl_class.set('rdf:ID', class_name)

            if labels:
                label_elem = ET.SubElement(owl_class, 'rdfs:label')
                label_elem.text = labels[0].get('Text', '')
                label_elem.set('xml:lang', 'en')

            # Store node style information as annotation
            style_data = node.find('.//{http://www.yworks.com/xml/yfiles-common/2.0}NodeStyle')
            if style_data is not None:
                annotation = ET.SubElement(owl_class, 'rdfs:comment')
                annotation.text = f"Original style: {ET.tostring(style_data, encoding='unicode')}"

            node_classes[node_id] = class_name

        # Second pass: create object properties from edges
        for edge in graph.findall('.//{http://graphml.graphdrawing.org/xmlns}edge'):
            edge_id = edge.get('id')
            source = edge.get('source')
            target = edge.get('target')

            if source in node_classes and target in node_classes:
                prop_name = f"has_connection_to_{target}"

                # Get edge label
                edge_labels = edge.findall('.//{http://www.yworks.com/xml/yfiles-common/2.0}Label')
                if edge_labels:
                    label_text = edge_labels[0].get('Text', '')
                    if label_text:
                        prop_name = self.sanitize_name(label_text) or prop_name

                # Create Object Property
                if prop_name not in object_properties:
                    obj_prop = ET.SubElement(owl_root, 'owl:ObjectProperty')
                    obj_prop.set('rdf:ID', prop_name)

                    if edge_labels and edge_labels[0].get('Text'):
                        label_elem = ET.SubElement(obj_prop, 'rdfs:label')
                        label_elem.text = edge_labels[0].get('Text')
                        label_elem.set('xml:lang', 'en')

                    object_properties[prop_name] = obj_prop

                # Create relation between classes
                source_class = node_classes[source]
                target_class = node_classes[target]

                # Add domain and range
                obj_prop = object_properties[prop_name]
                domain = ET.SubElement(obj_prop, 'rdfs:domain')
                domain.set('rdf:resource', f'#{source_class}')
                range_elem = ET.SubElement(obj_prop, 'rdfs:range')
                range_elem.set('rdf:resource', f'#{target_class}')

    def sanitize_name(self, name):
        if not name:
            return None
        # Remove invalid characters for OWL IDs
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        return sanitized if sanitized else None