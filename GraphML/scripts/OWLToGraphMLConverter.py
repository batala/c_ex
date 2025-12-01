class OWLToGraphMLConverter:
    def __init__(self):
        self.namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'y': 'http://www.yworks.com/xml/yfiles-common/2.0',
            'yx': 'http://www.yworks.com/xml/yfiles-common/4.0',
            'yjs': 'http://www.yworks.com/xml/yfiles-for-html/3.0/xaml',
            'x': 'http://www.yworks.com/xml/yfiles-common/markup/3.0'
        }

    def register_namespaces(self, root):
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)

    def convert(self, owl_file, graphml_file):
        # Parse OWL
        tree = ET.parse(owl_file)
        root = tree.getroot()

        # Create GraphML structure
        graphml = ET.Element('graphml')
        graphml.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')
        self.register_namespaces(graphml)

        # Add schema location
        graphml.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                   'http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml.html/2.0/ygraphml.xsd')

        # Define keys (similar to original)
        self.add_graphml_keys(graphml)

        # Add shared data
        self.add_shared_data(graphml)

        # Create main graph
        graph = ET.SubElement(graphml, 'graph')
        graph.set('id', 'G')
        graph.set('edgedefault', 'directed')

        # Process OWL classes and properties
        self.process_owl_elements(root, graph)

        # Write GraphML file
        tree = ET.ElementTree(graphml)
        with open(graphml_file, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
            f.write(b'<!--Created by yFiles for HTML 3.0.0.4-->\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

    def add_graphml_keys(self, graphml):
        keys = [
            ('d0', 'node', 'boolean', 'Expanded', 'http://www.yworks.com/xml/yfiles-common/2.0/folding/Expanded'),
            ('d1', 'node', 'string', 'NodeLabels', 'http://www.yworks.com/xml/yfiles-common/2.0/NodeLabels'),
            ('d2', 'node', 'string', 'NodeGeometry', 'http://www.yworks.com/xml/yfiles-common/2.0/NodeGeometry'),
            ('d3', 'all', 'string', 'UserTags', 'http://www.yworks.com/xml/yfiles-common/2.0/UserTags'),
            ('d4', 'node', 'string', 'NodeStyle', 'http://www.yworks.com/xml/yfiles-common/2.0/NodeStyle'),
            ('d5', 'node', 'string', 'NodeViewState', 'http://www.yworks.com/xml/yfiles-common/2.0/folding/1.1/NodeViewState'),
            ('d6', 'edge', 'string', 'EdgeLabels', 'http://www.yworks.com/xml/yfiles-common/2.0/EdgeLabels'),
            ('d7', 'edge', 'string', 'EdgeGeometry', 'http://www.yworks.com/xml/yfiles-common/2.0/EdgeGeometry'),
            ('d8', 'edge', 'string', 'EdgeStyle', 'http://www.yworks.com/xml/yfiles-common/2.0/EdgeStyle'),
            ('d9', 'edge', 'string', 'EdgeViewState', 'http://www.w3.org/2001/XMLSchema-instance/folding/1.1/EdgeViewState'),
            ('d10', 'port', 'string', 'PortLabels', 'http://www.yworks.com/xml/yfiles-common/2.0/PortLabels'),
            ('d11', 'port', 'string', 'PortLocationParameter', 'http://www.yworks.com/xml/yfiles-common/2.0/PortLocationParameter'),
            ('d12', 'port', 'string', 'PortStyle', 'http://www.yworks.com/xml/yfiles-common/2.0/PortStyle'),
            ('d13', 'port', 'string', 'PortViewState', 'http://www.yworks.com/xml/yfiles-common/2.0/folding/1.1/PortViewState'),
            ('d14', 'graphml', 'string', 'SharedData', 'http://www.yworks.com/xml/yfiles-common/2.0/SharedData')
        ]

        for key_id, for_attr, attr_type, attr_name, attr_uri in keys:
            key_elem = ET.SubElement(graphml, 'key')
            key_elem.set('id', key_id)
            key_elem.set('for', for_attr)
            key_elem.set('attr.type', attr_type)
            key_elem.set('attr.name', attr_name)
            key_elem.set('{http://www.yworks.com/xml/yfiles-common/2.0}attr.uri', attr_uri)

    def add_shared_data(self, graphml):
        data_elem = ET.SubElement(graphml, 'data')
        data_elem.set('key', 'd14')

        shared_data = ET.SubElement(data_elem, '{http://www.yworks.com/xml/yfiles-common/2.0}SharedData')

        # Add common style definitions
        self.add_style_definitions(shared_data)

    def add_style_definitions(self, shared_data):
        # Add font definition
        font = ET.SubElement(shared_data, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}Font')
        font.set('{http://www.yworks.com/xml/yfiles-common/2.0}Key', '7')
        font.set('fontSize', '12')
        font.set('lineSpacing', '0.2')

        # Add stroke definition
        stroke = ET.SubElement(shared_data, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}Stroke')
        stroke.set('{http://www.yworks.com/xml/yfiles-common/2.0}Key', '8')
        stroke.set('lineCap', 'SQUARE')
        stroke.set('thickness', '1.5')
        stroke_fill = ET.SubElement(stroke, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}Stroke.fill')
        css_fill = ET.SubElement(stroke_fill, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}CssFill')
        css_fill.set('cssString', '#662b00')

        # Add fill definition
        fill = ET.SubElement(shared_data, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}CssFill')
        fill.set('{http://www.yworks.com/xml/yfiles-common/2.0}Key', '9')
        fill.set('cssString', '#ff6c00')

        # Add arrow definition
        arrow = ET.SubElement(shared_data, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}Arrow')
        arrow.set('{http://www.yworks.com/xml/yfiles-common/2.0}Key', '10')
        arrow.set('fill', 'BLACK')
        arrow.set('type', 'NONE')

    def process_owl_elements(self, owl_root, graph):
        classes = {}
        properties = []

        # Extract classes
        for owl_class in owl_root.findall('.//{http://www.w3.org/2002/07/owl#}Class'):
            class_id = owl_class.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}ID')
            if class_id:
                label_elem = owl_class.find('.//{http://www.w3.org/2000/01/rdf-schema#}label')
                label = label_elem.text if label_elem is not None else class_id
                classes[class_id] = {'label': label, 'id': f"n{len(classes)}"}

        # Extract object properties
        for obj_prop in owl_root.findall('.//{http://www.w3.org/2002/07/owl#}ObjectProperty'):
            prop_id = obj_prop.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}ID')
            if prop_id:
                domain_elem = obj_prop.find('.//{http://www.w3.org/2000/01/rdf-schema#}domain')
                range_elem = obj_prop.find('.//{http://www.w3.org/2000/01/rdf-schema#}range')

                if domain_elem is not None and range_elem is not None:
                    domain = domain_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', '')[1:]  # Remove #
                    range_class = range_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', '')[1:]  # Remove #

                    if domain in classes and range_class in classes:
                        label_elem = obj_prop.find('.//{http://www.w3.org/2000/01/rdf-schema#}label')
                        label = label_elem.text if label_elem is not None else prop_id

                        properties.append({
                            'id': prop_id,
                            'label': label,
                            'source': classes[domain]['id'],
                            'target': classes[range_class]['id']
                        })

        # Create nodes
        x_pos = 0
        for class_info in classes.values():
            node = ET.SubElement(graph, 'node')
            node.set('id', class_info['id'])

            # Add node labels
            labels_data = ET.SubElement(node, 'data')
            labels_data.set('key', 'd1')
            labels_list = ET.SubElement(labels_data, '{http://www.yworks.com/xml/yfiles-common/markup/3.0}List')

            label_elem = ET.SubElement(labels_list, '{http://www.yworks.com/xml/yfiles-common/2.0}Label')
            label_elem.set('Text', class_info['label'])
            label_elem.set('PreferredSize', '121,24')

            # Add geometry
            geom_data = ET.SubElement(node, 'data')
            geom_data.set('key', 'd2')
            geom_elem = ET.SubElement(geom_data, '{http://www.yworks.com/xml/yfiles-common/2.0}RectD')
            geom_elem.set('X', str(x_pos))
            geom_elem.set('Y', '0')
            geom_elem.set('Width', '60')
            geom_elem.set('Height', '40')
            x_pos += 100

            # Add style
            style_data = ET.SubElement(node, 'data')
            style_data.set('key', 'd4')
            style_elem = ET.SubElement(style_data, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}RectangleNodeStyle')
            style_elem.set('cornerSize', '3.5')
            style_elem.set('stroke', '{http://www.yworks.com/xml/yfiles-common/2.0}GraphMLReference 8')
            style_elem.set('fill', '{http://www.yworks.com/xml/yfiles-common/2.0}GraphMLReference 9')

            # Add ports
            ET.SubElement(node, 'port').set('name', 'p0')
            ET.SubElement(node, 'port').set('name', 'p1')

        # Create edges
        for i, prop in enumerate(properties):
            edge = ET.SubElement(graph, 'edge')
            edge.set('id', f'e{i}')
            edge.set('source', prop['source'])
            edge.set('target', prop['target'])
            edge.set('sourceport', 'p0')
            edge.set('targetport', 'p0')

            # Add edge labels
            labels_data = ET.SubElement(edge, 'data')
            labels_data.set('key', 'd6')
            labels_list = ET.SubElement(labels_data, '{http://www.yworks.com/xml/yfiles-common/markup/3.0}List')

            label_elem = ET.SubElement(labels_list, '{http://www.yworks.com/xml/yfiles-common/2.0}Label')
            label_elem.set('Text', prop['label'])
            label_elem.set('PreferredSize', '98,24')

            # Add style
            style_data = ET.SubElement(edge, 'data')
            style_data.set('key', 'd8')
            style_elem = ET.SubElement(style_data, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}PolylineEdgeStyle')
            style_elem.set('smoothingLength', '100')
            style_elem.set('sourceArrow', '{http://www.yworks.com/xml/yfiles-common/2.0}GraphMLReference 10')

            target_arrow = ET.SubElement(style_elem, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}PolylineEdgeStyle.targetArrow')
            arrow_elem = ET.SubElement(target_arrow, '{http://www.yworks.com/xml/yfiles-for-html/3.0/xaml}Arrow')
            arrow_elem.set('fill', 'BLACK')
            arrow_elem.set('type', 'TRIANGLE')