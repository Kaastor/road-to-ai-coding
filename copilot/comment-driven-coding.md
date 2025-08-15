Here’s a tight, practical cheat sheet for **Comment-driven code generation** with GitHub Copilot—based on Microsoft’s Learn module about Copilot’s code completion and how it uses comments to guide suggestions. ([Microsoft Learn][1])

---

# Comment-Driven Code Generation — Cheat Sheet

### What it is

Copilot reads your comments (inline, block, docstrings, TODOs) plus nearby code to infer your intent and generate context-aware code: full functions, algorithm implementations, variable names, and more. ([Microsoft Learn][1])

---

## Core Patterns (with examples)

### 1) Describe the function (docstring or block comment) → get full implementation

**When to use:** You know the signature/behavior you want.

**Python**

```python
def reverse_string(s: str) -> str:
    """
    Return the input string reversed.
    Handle None by returning an empty string.
    """
    # Copilot will suggest a full implementation based on this docstring
```

(Expect slice notation or equivalent, plus None handling.) ([Microsoft Learn][1])

**JavaScript**

```js
// sumNumbers(nums): return the sum of an array of numbers.
// Ignore non-numeric values.
function sumNumbers(nums) {
  // Copilot fills in logic guided by comment
}
```

---

### 2) Outline the algorithm steps → get step-by-step code

**When to use:** You know the approach, want the code scaffolded.

**Python (Bubble Sort)**

```python
# Implement bubble sort:
# 1) Repeat until no swaps.
# 2) Compare adjacent items.
# 3) Swap if out of order.
# 4) Early exit if a pass has no swaps.
def bubble_sort(arr):
    ...
```

Copilot follows your numbered steps to generate the loop and swap logic. ([Microsoft Learn][1])

---

### 3) Use TODOs for incremental build-out

**When to use:** You’re stubbing features and want Copilot to flesh them out.

**C#**

```csharp
// TODO: Parse ISO 8601 date string to DateTime.
// TODO: Return null for invalid input.
public static DateTime? ParseIsoDate(string input)
{
    // Copilot suggests parsing/try-parse logic
}
```

Copilot treats TODOs as intent signals and proposes code accordingly. ([Microsoft Learn][1])

---

### 4) Specify inputs/outputs and constraints → get precise logic

**When to use:** You need edge cases handled.

**TypeScript**

```ts
// sanitizeUsername(name):
// - Trim whitespace
// - Lowercase
// - Keep [a-z0-9_], replace others with '-'
// - Max length 20
function sanitizeUsername(name: string): string {
  // Copilot proposes a regex + truncation
}
```

---

### 5) Comment the data shape / API contract → get correct usage

**When to use:** You’re calling an API or shaping data.

**Python**

```python
# Fetch /users/:id and return:
# {
#   id: int, name: str, email: str,
#   created_at: ISO8601
# }
# Raise ValueError if 404.
def get_user(user_id: int) -> dict:
    ...
```

Copilot aligns implementation to the commented contract. ([Microsoft Learn][1])

---

### 6) Name things in comments → get better identifiers

**When to use:** You care about readability and naming.

**JavaScript**

```js
// List of the user's favorite books
const /* Copilot will suggest: favoriteBooks */ = [];
```

Copilot leverages your comment to pick descriptive variable names. ([Microsoft Learn][1])

---

### 7) State formatting/error-handling preferences → get style-matched code

**When to use:** You want code that fits your project patterns.

**Go**

```go
// readConfig:
// - Read JSON from path
// - Use 2-space indent when rewriting file
// - Return (Config, error), no panics
func readConfig(path string) (Config, error) {
    ...
}
```

Copilot adapts to your formatting, naming, and error style. ([Microsoft Learn][1])

---

### 8) Provide examples/tests in comments → get behavior-driven code

**When to use:** You like “spec first”.

**Python**

```python
# slugify("Hello, World!") -> "hello-world"
# slugify("  A_B  ") -> "a-b"
def slugify(text: str) -> str:
    ...
```

---

## Quick Usage Tips

* **Be explicit about intent.** Short, clear comments produce stronger completions than vague ones. ([Microsoft Learn][1])
* **Outline steps** for algorithms to guide structure. ([Microsoft Learn][1])
* **Use TODOs** to grow features iteratively. ([Microsoft Learn][1])
* **Document contracts** (inputs/outputs/errors) to align suggestions. ([Microsoft Learn][1])
* **Leverage naming hints** in comments for readable identifiers. ([Microsoft Learn][1])
* **Cycle suggestions:** Use Copilot’s multiple-suggestions pane (Alt/Option + \[ / ]) to pick the best variant for your comment. ([Microsoft Learn][1])

---

## Mini Reference — Comment Starters

* “**Implement** `foo(bar)` — returns …, throws … on …, O(n log n).”
* “**Algorithm:** 1) … 2) … 3) … (early exit …).”
* “**Contract:** input {…}, output {…}, on error return …”
* “**Style:** use snake\_case, no magic numbers, 2-space indent.”
* “**TODO:** validate args; **TODO:** retry with backoff; **TODO:** sanitize input.”
* “**Examples:** f(‘Hello’) -> …; f(‘’) -> …”

---

### Accepting/Editing Suggestions (IDE ergonomics)

* Accept full suggestion: **Tab / Enter** (varies by editor).
* Browse alternatives: **Alt+] / Alt+\[** (Windows/Linux), **Option+] / Option+\[** (macOS). ([Microsoft Learn][1])

---

If you want, I can turn this into a printable one-pager (PDF) or tailor the examples to a specific language/framework you use most.

[1]: https://learn.microsoft.com/en-us/training/modules/github-copilot-across-environments/2-code-completion-with-git-hub-copilot "Code completion with GitHub Copilot - Training | Microsoft Learn"
