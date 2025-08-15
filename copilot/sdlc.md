Here’s a compact, practical cheat sheet for using GitHub Copilot across the SDLC—built from Microsoft’s “AI in the Software Development Lifecycle (SDLC)” unit, then expanded with concrete prompts and examples. ([Microsoft Learn][1])

# Requirements analysis → quick prototypes & scaffolds

**What Copilot is good for:** turning high-level requirements into initial code structures, API shape ideas, and quick proofs of concept. ([Microsoft Learn][1])

**Prompts you can paste into Copilot Chat**

* “From this user story: *‘As a customer, I can save items for later’*, propose folders, file names, and stub functions for a TypeScript/Next.js app.”
* “Draft an OpenAPI 3.0 spec skeleton for a `/wishlist` resource with GET/POST/DELETE.”
* “Turn these acceptance criteria into function signatures and TODOs in Python.”

**Example (OpenAPI skeleton)**

```yaml
openapi: 3.0.3
info: { title: Wishlist API, version: 0.1.0 }
paths:
  /wishlist:
    get: { summary: List items, responses: { "200": { description: OK } } }
    post: { summary: Add item, requestBody: { required: true }, responses: { "201": { description: Created } } }
  /wishlist/{id}:
    delete: { summary: Remove item, parameters: [{ name: id, in: path, required: true }], responses: { "204": { description: No Content } } }
```

---

# Design & development → build faster, follow patterns

**What Copilot is good for:** boilerplate, best-practice patterns, optimizations, and translating ideas between languages. ([Microsoft Learn][1])

**Prompts**

* “Implement a Repository pattern for `WishlistItem` in C# with async methods, cancellation tokens, and DI-ready constructor.”
* “Refactor this function for clarity and performance; add docstrings and a short complexity note.”
* “Translate this Python list-comprehension solution into Go idiomatic code.”

**Example (Repo pattern, TypeScript)**

```ts
// wishlist.repo.ts
export interface WishlistItem { id: string; sku: string; addedAt: Date }
export interface WishlistRepo {
  add(item: Omit<WishlistItem, "id"|"addedAt">): Promise<WishlistItem>;
  list(): Promise<WishlistItem[]>;
  remove(id: string): Promise<void>;
}

export class InMemoryWishlistRepo implements WishlistRepo {
  private db: Map<string, WishlistItem> = new Map();
  async add(i: Omit<WishlistItem, "id"|"addedAt">) {
    const item = { ...i, id: crypto.randomUUID(), addedAt: new Date() };
    this.db.set(item.id, item); return item;
  }
  async list() { return [...this.db.values()]; }
  async remove(id: string) { this.db.delete(id); }
}
```

---

# Testing & QA → generate tests, data, and edge cases

**What Copilot is good for:** test case stubs, realistic test data, edge-case ideas, and assertion suggestions. ([Microsoft Learn][1])

**Prompts**

* “Write `pytest` unit tests for `add_to_wishlist(user_id, sku)` covering: happy path, duplicate SKUs, invalid SKU, and capacity limit of 100.”
* “Generate table-driven tests in Go for `ValidateSKU` with boundary cases.”
* “Suggest property-based tests for a cart *total* function.”

**Example (pytest)**

```python
# test_wishlist.py
import pytest

def test_add_happy_path(repo):
    item = repo.add("u123", "SKU-1")
    assert item["sku"] == "SKU-1"

def test_add_duplicate_disallowed(repo):
    repo.add("u123", "SKU-1")
    with pytest.raises(ValueError):
        repo.add("u123", "SKU-1")

@pytest.mark.parametrize("sku", ["", None, "   "])
def test_invalid_sku(repo, sku):
    with pytest.raises(ValueError):
        repo.add("u123", sku)
```

---

# Deployment → scripts, configs, pipelines

**What Copilot is good for:** config files, deployment scripts, and docs tweaks for releasing. ([Microsoft Learn][1])

**Prompts**

* “Create a multi-stage Dockerfile for a Node 20 + pnpm app with a smaller runtime image.”
* “Draft a GitHub Actions workflow that runs tests, caches deps, builds Docker, and pushes to GHCR on tags.”
* “Write a Kubernetes `Deployment` and `Service` YAML for the wishlist API with rolling updates.”

**Examples**

```dockerfile
# Dockerfile (multi-stage)
FROM node:20 AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm i --frozen-lockfile
COPY . .
RUN pnpm build

FROM gcr.io/distroless/nodejs20
WORKDIR /app
COPY --from=build /app/dist ./dist
CMD ["dist/server.js"]
```

```yaml
# .github/workflows/ci.yml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'pnpm' }
      - run: corepack enable && pnpm i --frozen-lockfile
      - run: pnpm test -- --ci
```

---

# Maintenance & support → understand, fix, and modernize

**What Copilot is good for:** bug-fix suggestions, refactors, documentation, and helping decode legacy code. ([Microsoft Learn][1])

**Prompts**

* “Explain what this legacy function does line-by-line and suggest a safer, modern equivalent.”
* “Refactor for readability and add structured logging; keep behavior identical; include before/after complexity comments.”
* “Given this stack trace, propose 3 likely fixes and a minimal reproduction test.”

**Example (docstring + small refactor)**

```python
def normalize_sku(raw: str) -> str:
    """
    Normalize a SKU by trimming, uppercasing, and collapsing internal spaces.
    Raises:
        ValueError: if the SKU is empty after normalization.
    """
    sku = " ".join(raw.split()).upper()
    if not sku:
        raise ValueError("SKU cannot be empty")
    return sku
```

---

## Prompt patterns that make Copilot shine

* **Give context first:** “We use FastAPI, Pydantic v2, and Postgres via SQLAlchemy. Target Python 3.12.…”
* **State constraints:** “No external deps; O(n log n) or better; add docstrings and examples.”
* **Ask for diffs/tests:** “Propose a patch and the matching unit tests.”
* **Iterate:** follow up with “tighten this,” “fewer allocations,” or “convert to async.”
* **Review everything:** Copilot boosts speed, but developers must validate outputs and decisions.

---

**Source:** Microsoft Learn—*AI in the Software Development Lifecycle (SDLC)* unit summarizing where Copilot helps across requirements, design/development, testing, deployment, and maintenance. ([Microsoft Learn][1])

If you want, I can tailor this to your stack (language, framework, CI/CD) and turn it into a printable one-pager.

[1]: https://learn.microsoft.com/en-us/training/modules/developer-use-cases-for-ai-with-github-copilot/4-ai-software-development-lifecycle "AI in the Software Development Lifecycle (SDLC) - Training | Microsoft Learn"
