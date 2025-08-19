def hello(name: str | None = None) -> str:
    return f"Hello, {name or 'World'}!"

def main() -> None:
    # tiny CLI: python -m helloworld [name]
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else None
    print(hello(name))

if __name__ == "__main__":
    main()
