# Проект aiknd-ontology

## Назначение раздела описание онтологии для конвертера graphml<->owl для проекта ДИТ.Онтология

### Онтология на языке OWL (Web Ontology Language), описывающей структуру GraphML без элемента <hyperedge>. Онтология определена с использованием Turtle и использует URI-пространство http://ont.mos.ru/graphml.
####Основные особенности онтологии:
        Классы:
            Node, Edge, Graph, Key, Data — представляют основные элементы GraphML.
        Свойства:
            hasNode, hasEdge — связывают граф с его узлами и рёбрами.
            source, target — определяют направленность рёбер.
            hasKey, keyId, value — описывают атрибуты (<data>).
            attrName, attrType, forElement — описывают ключи (<key>).
        Примитивные типы (xsd:string, xsd:boolean) используются для атрибутов.