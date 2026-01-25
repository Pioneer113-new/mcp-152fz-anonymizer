import spacy
from presidio_analyzer.nlp_engine import SpacyNlpEngine, NerModelConfiguration
from analyzer_setup import create_analyzer_engine


def debug_mapping():
    print("--- Debugging SpacyNlpEngine Mapping ---")

    # Recreate the logic from analyzer_setup to test isolation
    ner_config = NerModelConfiguration(
        labels_to_ignore=["O"],
        model_to_presidio_entity_mapping={
            "PER": "PERSON",
            "LOC": "LOCATION",
            "ORG": "ORGANIZATION",
            "MISC": "O",
        },
        low_score_entity_names=[],
    )

    nlp_engine = SpacyNlpEngine(
        models=[{"lang_code": "ru", "model_name": "ru_core_news_lg"}],
        ner_model_configuration=ner_config,
    )
    nlp_engine.load()

    text = "Меня зовут Иван Петров."
    nlp_artifacts = nlp_engine.process_text(text, language="ru")

    print(f"Text: {text}")
    print("Entities found by NLP Engine (Mapped):")
    for ent in nlp_artifacts.entities:
        print(f" - Entity: {ent}")

    print("\n--- Running Analyzer ---")
    analyzer = create_analyzer_engine()
    results = analyzer.analyze(text=text, language="ru")
    print("Analyzer Results:")
    for res in results:
        print(res)


if __name__ == "__main__":
    debug_mapping()
