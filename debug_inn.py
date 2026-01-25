from main import audit_text, analyzer


def debug_inn():
    text = "ИНН компании 7707083893"
    print(f"Analyzing: {text}")
    results = analyzer.analyze(text=text, language="ru")
    for res in results:
        print(res)


if __name__ == "__main__":
    debug_inn()
