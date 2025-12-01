def main():
    # Конвертация GraphML в OWL
    converter_to_owl = GraphMLToOWLConverter()
    converter_to_owl.convert('onto_ed.xml', 'ontology.owl')
    print("Конвертация GraphML → OWL завершена")

    # Конвертация OWL обратно в GraphML
    converter_to_graphml = OWLToGraphMLConverter()
    converter_to_graphml.convert('ontology.owl', 'restored_graphml.xml')
    print("Конвертация OWL → GraphML завершена")

    print("Процесс завершен успешно!")

if __name__ == "__main__":
    main()