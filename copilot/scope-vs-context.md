Here’s your **GitHub Copilot Chat Cheat Sheet** for `@` commands and `#` context references — compact enough to keep by your desk, but detailed enough so you never forget what each one does.

---

## **`@` Commands** (set the *scope* of the conversation)

Use at the **start of your prompt** to tell Copilot where to look.

| Command          | Scope / Purpose                                                                                       | Example                                                      |
| ---------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **`@workspace`** | Loads your **entire project/workspace** into context (all non-.gitignored files, structure, symbols). | `@workspace Give me an overview of all data models.`         |
| **`@vscode`**    | Questions about the **VS Code editor** itself.                                                        | `@vscode How do I enable autosave?`                          |
| **`@terminal`**  | Helps with **shell/CLI commands**.                                                                    | `@terminal Show me the command to check my Node.js version.` |
| **`@github`**    | Pulls from **GitHub context** — issues, PRs, discussions in the linked repo.                          | `@github Summarize open pull requests.`                      |
| **`@tests`**     | Focuses on test-related files and logic in your workspace.                                            | `@tests Show me failing test cases.`                         |
| **`@editor`**    | Interacts with **current editor selection or active file** explicitly.                                | `@editor Explain the selected function.`                     |

---

## **`#` Context References** (pull in *specific files/symbols*)

Use **anywhere in your prompt** to reference a file, folder, symbol, or special scope.

| Reference           | What it does                                               | Example                                            |
| ------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| **`#filename.ext`** | Adds that file’s content to the prompt.                    | `Explain the logic in #auth.js`                    |
| **`#FolderName/`**  | Adds all files in that folder.                             | `List classes in #services/`                       |
| **`#SymbolName`**   | Refers to a class, function, or variable in your codebase. | `Where is #UserController used?`                   |
| **`#codebase`**     | Searches the entire workspace for relevant code.           | `Show me where login is implemented in #codebase.` |
| **`#tests`**        | Focuses on test files only.                                | `List all unit tests in #tests.`                   |

---

## **Key Differences**

* `@workspace` changes the **whole conversation scope** — everything you ask in that prompt uses workspace-wide context.
* `#codebase` is **surgical** — it only brings in the codebase when that specific word appears.
* You can combine them:
  `@workspace Explain how #UserService interacts with #AuthController.`

---

## **Pro Tips**

* If you just open multiple files, Copilot **won’t** automatically use them all — you must attach them via drag-and-drop, `#filename`, or a wide scope like `@workspace`/`#codebase`.
* Keep prompts clear about **what** you want and **where** to look — Copilot context is powerful but not psychic.
* In multi-step work, start with `@workspace` for an overview, then switch to `#codebase` or `#filename` for deep dives.

---

I can also make you a **one-page PDF version** of this cheat sheet with visual examples and syntax highlights so you can keep it next to your editor.
Do you want me to make that?
