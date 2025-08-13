Here’s a comprehensive overview of **GitHub Copilot inline‑chat commands** along with descriptions—great to have all in one place! These apply primarily when using Copilot Chat in Visual Studio Code or Visual Studio, and the exact commands may vary by IDE.

---

## Slash Commands (Trigger by typing `/` in the chat input)

These let you quickly perform common tasks without writing full prompts:

| Command           | Description                                                               |
| ----------------- | ------------------------------------------------------------------------- |
| `/explain`        | Explain the selected or active code block ([GitHub Docs][1])              |
| `/fix`            | Propose a fix for problems in the selected code ([GitHub Docs][1])        |
| `/fixTestFailure` | Find and fix a failing test ([GitHub Docs][1])                            |
| `/tests`          | Generate unit tests for the selected code ([GitHub Docs][1])              |
| `/help`           | Show quick reference and basics for using Copilot Chat ([GitHub Docs][1]) |
| `/new`            | Start a new project or conversation ([GitHub Docs][1])                    |
| `/clear`          | Clear the current conversation ([GitHub Docs][1])                         |

Note: Available slash commands *may vary depending on your environment and IDE* — use `/` in the prompt box to see what's supported locally. ([GitHub Docs][1])

---

## Chat Variables (Add context using `#` in prompt)

Insert code-related context into your prompt to help Copilot understand scope:

* `#block` — Includes the current code block
* `#class` — Includes the current class context
* `#comment` — Includes the current comment
* `#file` — Includes the entire current file
* `#function` — Includes the current function or method
* `#line` — Includes the current line of code
* `#path` — Includes the file path
* `#project` — Includes project-wide context
* `#selection` — Includes whatever text you’ve selected
* `#sym` — Includes the current symbol in focus ([Microsoft Learn][2], [GitHub Docs][1], [Microsoft Learn][3])

---

## Chat Participants (Context-specific helpers via `@`)

Invoke specific “participants” to bring in domain-aware help:

* `@azure` — Context about Azure services (in preview)
* `@github` — GitHub‑specific Copilot skills
* `@terminal` — Helps with terminal and shell commands
* `@vscode` — Tips around using Visual Studio Code
* `@workspace` — Offers understanding from your entire codebase ([GitHub Docs][1])

---

## Shortcuts & Interaction Triggers

### VS Code Inline Chat & Quick Chat

* **Inline chat**: Press `⌘I` (Mac) / `Ctrl + I` (Win/Linux) to open a chat at your cursor or in the terminal context ([GitHub Docs][4])
* **Quick Chat**: Use `⇧⌥⌘L` (Mac) / `Ctrl + Shift + Alt + L` (Win/Linux) for fast query without opening full chat view ([GitHub Docs][4])

### Smart Actions (VS Code)

Right-click in the editor → choose **"Copilot"** → pick an action like `Ask Copilot` directly from context menus or via the sparkle icon when selecting code ([GitHub Docs][4])

### Visual Studio Inline Chat

* Trigger inline chat by **right-clicking** in your editor and choosing **"Ask Copilot"** ([Microsoft Learn][3])
* The inline chat window lets you see responses inline with code, with options to continue in full chat pane or dismiss with `Esc` ([Microsoft Learn][3])

---

## Summary at a Glance

* **Slash Commands** (`/explain`, `/fix`, `/tests`, etc.) — Fast common actions
* **Chat Variables** (`#file`, `#selection`, `#project`, etc.) — Provide context to your prompt
* **Chat Participants** (`@github`, `@terminal`, `@azure`, etc.) — Context-aware domain assistance
* **Keyboard Shortcuts** — For quick inline interactions (e.g. `Ctrl + I`, Quick Chat)
* **Smart Actions & Context Menus** — Convenient prompt entry inside IDE
* **Inline Chat vs Chat Pane** — Keep workflow smooth with in-editor suggestions or immersive view

---

**Tip:** Use `/` in your chat input to view the exact commands supported in your setup—and experiment with combining variables and commands for powerful prompts (e.g. `/explain #function`). Let me know if you'd like examples or tailored prompt ideas!

[1]: https://docs.github.com/en/copilot/reference/cheat-sheet?utm_source=chatgpt.com "GitHub Copilot Chat cheat sheet"
[2]: https://learn.microsoft.com/en-us/visualstudio/ide/copilot-chat-context?view=vs-2022&utm_source=chatgpt.com "Customize chat responses - Visual Studio (Windows)"
[3]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-chat?view=vs-2022&utm_source=chatgpt.com "About GitHub Copilot Chat in Visual Studio"
[4]: https://docs.github.com/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide?utm_source=chatgpt.com "Asking GitHub Copilot questions in your IDE"
