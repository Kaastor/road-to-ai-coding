Here’s a compact list of the techniques from that Microsoft Learn page, each with a quick, practical example you can paste into Copilot/Chat. ([Microsoft Learn][1])

# Foundations: the “4 Ss”

* **Single** — Ask for one thing.

  * *Prompt:* “Write a Python function `is_prime(n: int) -> bool`. Don’t print—just return True/False.”
* **Specific** — Spell out constraints, language, APIs, etc.

  * *Prompt:* “In TypeScript, make a pure function `groupBy<T>(items: T[], key: keyof T): Record<string, T[]>`. No external libs. O(n) time.”
* **Short** — Be concise but complete.

  * *Prompt:* “Python 3.12. Validate RFC-5322 email with `re`. Return `bool`.”
* **Surround (context)** — Provide context via filenames, comments, or nearby code (Copilot also reads open files/tabs).

  * *Prompt (as a file header comment):*

    ```py
    # file: analytics/cleaning.py
    # Input: pandas 2.x DataFrame with columns ["user_id","ts","event"]
    # Task: drop dup events per user per minute, keep earliest ts
    # Output: function dedupe_events(df)->DataFrame (same schema)
    ```

  Copilot uses these details to tailor suggestions. ([Microsoft Learn][1])

# Best practices

* **Provide enough clarity** — Combine “Single” + “Specific.”

  * *Prompt:* “Write a Python function `filter_even(nums: list[int]) -> list[int]` using a list comprehension. Include a docstring and one `pytest` case.”
* **Provide enough context with details** — Give environment, steps, or assumptions.

  * *Prompt:*

    ```py
    # We use FastAPI on Python 3.12. Add an endpoint GET /health that returns {"status":"ok"}.
    # Steps:
    # 1) Create router in health.py
    # 2) Include in app.py
    # 3) Add minimal test with httpx.AsyncClient
    ```
* **Provide examples for learning** — Show the shape of inputs/outputs.

  * *Prompt:*

    ```
    Write a function `slugify(title: str)->str`.
    Examples:
    "Hello, World!" -> "hello-world"
    "Café crème"    -> "cafe-creme"
    "  A/B Testing "-> "a-b-testing"
    Use only stdlib.
    ```
* **Assert & iterate** — Treat it like a dialogue: refine after the first draft.

  * *Initial prompt:* “Generate a Node.js script that reads CSV and prints JSON.”
  * *Follow-up refinement:* “Great start. Now: stream large files, infer types, and add `--out` flag. Include a usage example and one Jest test.” ([Microsoft Learn][1])

# How Copilot “learns” from your prompt (prompting modes)

* **Zero-shot** — No examples, just a clear instruction.

  * *Prompt:* “Write a function to convert Celsius ↔ Fahrenheit in Python. Include type hints and doctests.”
* **One-shot** — Provide one example to set the pattern.

  * *Prompt:*

    ```
    Example:
    def to_celsius(f: float)->float:
        return (f - 32) * 5/9

    Now write the inverse:
    def to_fahrenheit(c: float)->float: ...
    ```
* **Few-shot** — Provide several examples to shape style/behavior.

  * *Prompt:*

    ````
    Write greet(hour:int)->str.
    Examples:
    8  -> "Good morning"
    14 -> "Good afternoon"
    20 -> "Good evening"
    2  -> "Good night"
    Keep it locale-agnostic and add tests.
    ``` :contentReference[oaicite:3]{index=3}
    ````

If you want, tell me your stack (languages, frameworks, testing tools), and I’ll tailor these examples to your exact setup.

[1]: https://learn.microsoft.com/en-us/training/modules/introduction-prompt-engineering-with-github-copilot/2-prompt-engineering-foundations-best-practices "Prompt engineering foundations and best practices - Training | Microsoft Learn"
