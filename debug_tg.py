from main import analyzer


def debug_tg():
    text = "Группа в телеграм с id -1001234567890"
    print(f"Analyzing: {text}")
    results = analyzer.analyze(text=text, language="ru")
    for res in results:
        print(res)


if __name__ == "__main__":
    debug_tg()
