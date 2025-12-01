import { Parser, Writer, DataFactory } from 'n3';
import { DOMParser, XMLSerializer } from 'xmldom';
import * as fs from 'fs';

// === Используем DataFactory для создания термов ===
const { namedNode, literal, defaultGraph } = DataFactory;

// === Онтология (NS) ===
const NS = {
    graphml: 'http://example.org/graphml#',
    rdf: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    rdfs: 'http://www.w3.org/2000/01/rdf-schema#',
    owl: 'http://www.w3.org/2002/07/owl#',
    xsd: 'http://www.w3.org/2001/XMLSchema#',
    xml: 'http://www.w3.org/XML/1998/namespace'
};

// === GraphML → RDF ===
export function graphmlToRDF(graphmlString) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(graphmlString, 'application/xml');

    const quads = [];
    const baseIRI = 'http://example.org/graphml-instance#';

    // Извлекаем ключи
    const keys = {};
    const keyElements = xmlDoc.getElementsByTagName('key');
    for (let i = 0; i < keyElements.length; i++) {
        const keyElem = keyElements[i];
        const id = keyElem.getAttribute('id');
        const forAttr = keyElem.getAttribute('for');
        const attrName = keyElem.getAttribute('attr.name');
        const attrType = keyElem.getAttribute('attr.type');
        keys[id] = { id, for: forAttr, name: attrName, type: attrType };
    }

    // GraphML документ
    const graphmlElem = xmlDoc.documentElement;
    const docIRI = `${baseIRI}doc1`;
    quads.push(
        namedNode(docIRI),
        namedNode(`${NS.rdf}type`),
        namedNode(`${NS.graphml}GraphML`),
        defaultGraph()
    );

    // Graph
    const graphElems = xmlDoc.getElementsByTagName('graph');
    if (graphElems.length > 0) {
        const graphElem = graphElems[0];
        const graphId = graphElem.getAttribute('id') || 'G';
        const graphIRI = `${baseIRI}${graphId}`;
        quads.push(
            namedNode(docIRI),
            namedNode(`${NS.graphml}hasGraph`),
            namedNode(graphIRI),
            defaultGraph()
        );
        quads.push(
            namedNode(graphIRI),
            namedNode(`${NS.rdf}type`),
            namedNode(`${NS.graphml}Graph`),
            defaultGraph()
        );
        quads.push(
            namedNode(graphIRI),
            namedNode(`${NS.graphml}edgeDefault`),
            literal(graphElem.getAttribute('edgedefault') || 'undirected'),
            defaultGraph()
        );

        // Узлы
        const nodeElems = graphElem.getElementsByTagName('node');
        for (let i = 0; i < nodeElems.length; i++) {
            const nodeElem = nodeElems[i];
            const nodeId = nodeElem.getAttribute('id');
            const nodeIRI = `${baseIRI}${nodeId}`;
            quads.push(
                namedNode(graphIRI),
                namedNode(`${NS.graphml}hasNode`),
                namedNode(nodeIRI),
                defaultGraph()
            );
            quads.push(
                namedNode(nodeIRI),
                namedNode(`${NS.rdf}type`),
                namedNode(`${NS.graphml}Node`),
                defaultGraph()
            );
            quads.push(
                namedNode(nodeIRI),
                namedNode(`${NS.graphml}id`),
                literal(nodeId),
                defaultGraph()
            );

            // Данные узла
            const dataElems = nodeElem.getElementsByTagName('data');
            for (let j = 0; j < dataElems.length; j++) {
                const dataElem = dataElems[j];
                const keyId = dataElem.getAttribute('key');
                const value = dataElem.textContent?.trim() || '';
                const keyDef = keys[keyId];
                if (!keyDef) {
                    console.warn(`Unknown key referenced: ${keyId}`);
                    continue;
                }
                const dataIRI = `${baseIRI}${nodeId}_data_${keyId}`;
                quads.push(
                    namedNode(nodeIRI),
                    namedNode(`${NS.graphml}hasData`),
                    namedNode(dataIRI),
                    defaultGraph()
                );
                quads.push(
                    namedNode(dataIRI),
                    namedNode(`${NS.rdf}type`),
                    namedNode(`${NS.graphml}Data`),
                    defaultGraph()
                );
                quads.push(
                    namedNode(dataIRI),
                    namedNode(`${NS.graphml}value`),
                    literal(value),
                    defaultGraph()
                );
                quads.push(
                    namedNode(dataIRI),
                    namedNode(`${NS.graphml}hasKey`),
                    namedNode(`${baseIRI}key_${keyId}`),
                    defaultGraph()
                );
            }
        }

        // Рёбра
        const edgeElems = graphElem.getElementsByTagName('edge');
        for (let i = 0; i < edgeElems.length; i++) {
            const edgeElem = edgeElems[i];
            const edgeId = edgeElem.getAttribute('id');
            const sourceId = edgeElem.getAttribute('source');
            const targetId = edgeElem.getAttribute('target');
            const edgeIRI = `${baseIRI}${edgeId}`;
            quads.push(
                namedNode(graphIRI),
                namedNode(`${NS.graphml}hasEdge`),
                namedNode(edgeIRI),
                defaultGraph()
            );
            quads.push(
                namedNode(edgeIRI),
                namedNode(`${NS.rdf}type`),
                namedNode(`${NS.graphml}Edge`),
                defaultGraph()
            );
            quads.push(
                namedNode(edgeIRI),
                namedNode(`${NS.graphml}id`),
                literal(edgeId),
                defaultGraph()
            );
            quads.push(
                namedNode(edgeIRI),
                namedNode(`${NS.graphml}hasSource`),
                namedNode(`${baseIRI}${sourceId}`),
                defaultGraph()
            );
            quads.push(
                namedNode(edgeIRI),
                namedNode(`${NS.graphml}hasTarget`),
                namedNode(`${baseIRI}${targetId}`),
                defaultGraph()
            );

            // Данные рёбер
            const dataElems = edgeElem.getElementsByTagName('data');
            for (let j = 0; j < dataElems.length; j++) {
                const dataElem = dataElems[j];
                const keyId = dataElem.getAttribute('key');
                const value = dataElem.textContent?.trim() || '';
                const keyDef = keys[keyId];
                if (!keyDef) {
                    console.warn(`Unknown key referenced: ${keyId}`);
                    continue;
                }
                const dataIRI = `${baseIRI}${edgeId}_data_${keyId}`;
                quads.push(
                    namedNode(edgeIRI),
                    namedNode(`${NS.graphml}hasData`),
                    namedNode(dataIRI),
                    defaultGraph()
                );
                quads.push(
                    namedNode(dataIRI),
                    namedNode(`${NS.rdf}type`),
                    namedNode(`${NS.graphml}Data`),
                    defaultGraph()
                );
                quads.push(
                    namedNode(dataIRI),
                    namedNode(`${NS.graphml}value`),
                    literal(value),
                    defaultGraph()
                );
                quads.push(
                    namedNode(dataIRI),
                    namedNode(`${NS.graphml}hasKey`),
                    namedNode(`${baseIRI}key_${keyId}`),
                    defaultGraph()
                );
            }
        }
    }

    console.log('Generated quads:', quads.length); // ✅
    return quads;
}

// === RDF → GraphML ===
export function rdfToGraphML(quads) {
    const serializer = new XMLSerializer();
    const doc = new DOMParser().parseFromString('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"></graphml>', 'application/xml');
    const graphml = doc.documentElement;

    // Извлекаем ключи
    const keyQuads = quads.filter(q =>
        q.predicate.value === `${NS.rdf}type` &&
        q.object.value === `${NS.graphml}Key`
    );

    const keysMap = new Map();

    for (const quad of keyQuads) {
        const keyIRI = quad.subject.value;
        const idQuad = quads.find(q => q.subject.value === keyIRI && q.predicate.value === `${NS.graphml}id`);
        const forQuad = quads.find(q => q.subject.value === keyIRI && q.predicate.value === `${NS.graphml}for`);
        const nameQuad = quads.find(q => q.subject.value === keyIRI && q.predicate.value === `${NS.graphml}attrName`);
        const typeQuad = quads.find(q => q.subject.value === keyIRI && q.predicate.value === `${NS.graphml}attrType`);

        if (idQuad && forQuad && nameQuad && typeQuad) {
            keysMap.set(keyIRI, {
                id: idQuad.object.value,
                for: forQuad.object.value,
                name: nameQuad.object.value,
                type: typeQuad.object.value
            });
        }
    }

    // Создаём <key> элементы
    for (const [iri, key] of keysMap) {
        const keyElem = doc.createElement('key');
        keyElem.setAttribute('id', key.id);
        keyElem.setAttribute('for', key.for);
        keyElem.setAttribute('attr.name', key.name);
        keyElem.setAttribute('attr.type', key.type);
        graphml.appendChild(keyElem);
    }

    // Находим граф
    const graphQuad = quads.find(q => q.predicate.value === `${NS.graphml}hasGraph`);
    if (!graphQuad) {
        throw new Error('No graph found in RDF data.');
    }
    const graphIRI = graphQuad.object.value;

    const graph = doc.createElement('graph');
    graph.setAttribute('id', graphIRI.split('#').pop() || 'G');
    graph.setAttribute('edgedefault', 'directed');

    // Узлы
    const nodeQuads = quads.filter(q =>
        q.predicate.value === `${NS.graphml}hasNode` &&
        q.subject.value === graphIRI
    );

    for (const quad of nodeQuads) {
        const nodeIdIRI = quad.object.value;
        const nodeId = nodeIdIRI.split('#').pop();
        if (!nodeId) continue; // ✅ Проверяем, что nodeId не null/undefined

        const node = doc.createElement('node');
        node.setAttribute('id', nodeId);
        graph.appendChild(node);

        // Данные узла
        const dataQuads = quads.filter(q =>
            q.predicate.value === `${NS.graphml}hasData` &&
            q.subject.value === nodeIdIRI
        );

        for (const dataQuad of dataQuads) {
            const dataIRI = dataQuad.object.value;
            const valueQuad = quads.find(q => q.subject.value === dataIRI && q.predicate.value === `${NS.graphml}value`);
            const keyRefQuad = quads.find(q => q.subject.value === dataIRI && q.predicate.value === `${NS.graphml}hasKey`);

            if (valueQuad && keyRefQuad) {
                const keyId = keyRefQuad.object.value.split('#').pop().replace('key_', '');
                const dataElem = doc.createElement('data');
                dataElem.setAttribute('key', keyId);
                dataElem.textContent = valueQuad.object.value;
                node.appendChild(dataElem);
            }
        }
    }

    // Рёбра
    const edgeQuads = quads.filter(q =>
        q.predicate.value === `${NS.graphml}hasEdge` &&
        q.subject.value === graphIRI
    );

    for (const quad of edgeQuads) {
        const edgeIdIRI = quad.object.value;
        if (!edgeIdIRI) {
            console.warn('Edge IRI is undefined, skipping...');
            continue;
        }
        const edgeId = edgeIdIRI.split('#').pop();
        if (!edgeId) {
            console.warn(`Could not extract edge ID from IRI: ${edgeIdIRI}`);
            continue;
        }

        const sourceQuad = quads.find(q => q.subject.value === edgeIdIRI && q.predicate.value === `${NS.graphml}hasSource`);
        const targetQuad = quads.find(q => q.subject.value === edgeIdIRI && q.predicate.value === `${NS.graphml}hasTarget`);

        if (!sourceQuad || !targetQuad) {
            console.warn(`Missing source or target for edge ${edgeIdIRI}. Skipping.`);
            continue;
        }

        const sourceId = sourceQuad.object.value.split('#').pop();
        const targetId = targetQuad.object.value.split('#').pop();

        if (!sourceId || !targetId) {
            console.warn(`Could not extract source/target IDs for edge ${edgeId}. Skipping.`);
            continue;
        }

        const edge = doc.createElement('edge');
        edge.setAttribute('id', edgeId);
        edge.setAttribute('source', sourceId);
        edge.setAttribute('target', targetId);
        graph.appendChild(edge);

        // Данные рёбер
        const dataQuads = quads.filter(q =>
            q.predicate.value === `${NS.graphml}hasData` &&
            q.subject.value === edgeIdIRI
        );

        for (const dataQuad of dataQuads) {
            const dataIRI = dataQuad.object.value;
            const valueQuad = quads.find(q => q.subject.value === dataIRI && q.predicate.value === `${NS.graphml}value`);
            const keyRefQuad = quads.find(q => q.subject.value === dataIRI && q.predicate.value === `${NS.graphml}hasKey`);

            if (valueQuad && keyRefQuad) {
                const keyId = keyRefQuad.object.value.split('#').pop().replace('key_', '');
                const dataElem = doc.createElement('data');
                dataElem.setAttribute('key', keyId);
                dataElem.textContent = valueQuad.object.value;
                edge.appendChild(dataElem);
            }
        }
    }

    graphml.appendChild(graph);

    return serializer.serializeToString(graphml);
}

// === Пример использования ===
const exampleGraphML = `
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="name" for="node" attr.name="name" attr.type="string"/>
  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="directed">
    <node id="n0">
      <data key="name">Node A</data>
    </node>
    <node id="n1">
      <data key="name">Node B</data>
    </node>
    <edge id="e0" source="n0" target="n1">
      <data key="weight">2.5</data>
    </edge>
  </graph>
</graphml>
`;

console.log('GraphML -> RDF...');
const rdfQuads = graphmlToRDF(exampleGraphML);

if (rdfQuads.length === 0) {
    console.error('❌ No quads were generated from GraphML. Check the parsing logic.');
    process.exit(1);
}

console.log(`✅ Generated ${rdfQuads.length} quads.`);

const writer = new Writer({ format: 'text/turtle' });

for (const quad of rdfQuads) {
    writer.addQuad(quad);
}

writer.end((error, result) => {
    if (error) {
        console.error('❌ Error serializing RDF:', error);
    } else {
        console.log('✅ Serialization successful.');

        // === Сохраняем в файл ===
        fs.writeFileSync('output_rdf.ttl', result, 'utf8');
        console.log('✅ RDF saved to output_rdf.ttl');

        console.log('RDF -> GraphML...');
        const newGraphML = rdfToGraphML(rdfQuads);

        // === Сохраняем GraphML в файл ===
        fs.writeFileSync('output_graphml.xml', newGraphML, 'utf8');
        console.log('✅ GraphML saved to output_graphml.xml');
    }
});
