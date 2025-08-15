Here’s a compact, up-to-date **GitHub Copilot debugging cheat sheet** with the commands, what they do, and copy-pasteable examples you can use right inside VS Code (plus notes for JetBrains/Visual Studio where they differ).

---

# Core “debug with Copilot” moves

### Start or configure debugging

* **Create a debug configuration**
  Ask Copilot to scaffold `launch.json` for your app.
  *Example (Chat view)*:

  > Create a debug configuration for a Flask app that starts with `python app.py` and opens port 5000.
  > Copilot will propose a `launch.json` you can accept/tweak. ([Visual Studio Code][1])

* **One-liner: start a debug session from the terminal**
  Prefix your normal start command with `copilot-debug`.

  ```
  copilot-debug node app.js
  copilot-debug python manage.py runserver
  ```

  Copilot auto-configures and launches a debugging session. ([Visual Studio Code][1])

---

# Slash commands you’ll actually use to fix bugs

> Type `/` in Copilot Chat (or Inline Chat) to see what’s available in your environment.

| Command                     | What it does                                                                                   | Quick examples                                                                                                     |
| --------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `/fix`                      | Proposes a fix for the selected code or active editor.                                         | “/fix” after selecting a failing function. Or: “/fix: this throws on null inputs—make it safe.” ([GitHub Docs][2]) |
| `/explain`                  | Explains selected code or the file—great for understanding cryptic logic before you change it. | “/explain why this recursion never terminates.” ([GitHub Docs][2])                                                 |
| `/fixTestFailure` (VS Code) | Finds and fixes a failing test.                                                                | “/fixTestFailure: Jest test `adds()` fails on negative numbers.” ([GitHub Docs][2])                                |
| `/tests`                    | Generates unit tests for the selected code—useful to pin the bug before you fix it.            | “/tests for `calculatePrice()` incl. edge cases (0, negative, NaN).” ([GitHub Docs][2])                            |
| `/optimize` (VS / VS Code)  | Analyzes and improves runtime for the selection—good for “it works but is slow.”               | “/optimize: this loop is O(n²); make it linear if possible.” ([GitHub Docs][2])                                    |

* JetBrains & Xcode also support `/fix`, `/explain`, `/tests` (names are the same). Visual Studio adds `/doc`, `/optimize`. Availability varies slightly per IDE. ([GitHub Docs][2])

---

# Context boosters (they make debugging answers better)

Use these right inside messages:

* **Chat variables**: `#selection`, `#file`, `#function`, `#class`, `#project`, `#line`, `#path`, `#block`, `#sym` to inject precise code context.
  *Example*:

  > Why does this throw `TypeError` in #selection? Suggest a fix and tests.
  > Compare #file to #file\:utils/helpers.ts and dedupe overlapping functions. ([GitHub Docs][2])

* **Participants**:
  `@workspace` (project-wide code context), `@terminal` (shell/CLI context), `@vscode` (VS Code features), `@github` (repo/PR/issues context).
  *Example*:

  > @workspace Find where we parse dates and why `YYYY-MM-DD` fails on Safari.
  > @terminal The command `curl ...` returns 429—suggest retries/backoff. ([GitHub Docs][2])

* **Mentions**: Attach issues, PRs, or files with `@` to give Copilot extra context while it reasons about a bug. ([GitHub Docs][2])

---

# High-leverage debugging prompts

These are ready to paste (use Inline Chat on a selection or Chat view):

1. **Explain & pinpoint**

   > Explain in depth why my code produces this error and how to fix it:
   > `TypeError: can only concatenate str (not "int") to str`
   > Include a minimal patch.
   > *Why*: Classic first step that yields cause + fix suggestion. ([GitHub Docs][3])

2. **Incorrect output (no exception)**

   > The output of #file is much higher than expected (should be 720 for 6!). Walk through the logic, identify the bug, and propose a corrected implementation with tests. ([GitHub Docs][3])

3. **Make it fail, then fix it (TDD style)**

   > Generate unit tests for #selection that capture the current bug (edge cases: empty input, null, negative). Then propose a fix that makes the tests pass.
   > Use `/tests` first, then `/fix`. ([GitHub Docs][2])

4. **Stuck trace triage**

   > Given this stack trace and #file, map each frame to source lines, identify the root cause, and suggest a minimal change.
   > Paste the trace; add `#selection` for the hot code. (General Copilot Chat usage.) ([GitHub Docs][4])

5. **Terminal & runtime errors**

   > @terminal I’m getting `ECONNRESET` when running `npm start`. Show likely causes, add retries with exponential backoff, and update code where appropriate. ([GitHub Docs][2])

---

# Cookbook: common error patterns

* **Invalid / malformed JSON**
  Ask Copilot to validate and repair JSON, or to generate robust parsing with schema checks.
  *Prompt*:

  > The API returns sometimes-invalid JSON (dangling commas). Show defensive parsing and fallback handling.
  > Copilot can suggest validators and tolerant parsing strategies. ([GitHub Docs][5])

* **429 / rate limiting**
  *Prompt*:

  > When the API returns 429, implement retries with exponential backoff and jitter; cap at 5 attempts and surface a meaningful error. Provide language-idiomatic code. ([GitHub Docs][5])

---

# Fixing code without writing prompts

* **Smart Action (VS Code)**: select code → Right-click **Generate Code → Fix** to get an inline fix suggestion; refine in chat if needed.

  * Or use Inline Chat (`Ctrl/Cmd+I`) → type `/fix`. ([Visual Studio Code][1])

---

# Minimal debug workflow (VS Code)

1. **Reproduce** the bug; grab the stack trace or wrong output.
2. **Scope** the code: select the suspicious function/lines.
3. **Generate tests** (`/tests`) to pin behavior.
4. **Ask for a fix** (`/fix`), or **explain** first (`/explain`).
5. **Run with `copilot-debug`** to start an instrumented session if you don’t have `launch.json` yet.
6. **Iterate** until tests pass and performance is acceptable (`/optimize` if needed). ([GitHub Docs][2], [Visual Studio Code][1])

---

# Extra tips

* You can use these same techniques on **beginner debugging tutorials** that walk you through error-first and wrong-output cases (Python example, but the pattern generalizes). ([GitHub Docs][3])
* There’s a short **VS Code guide** dedicated to debugging with Copilot (covers `copilot-debug`, `/startDebugging`, Smart Actions). Worth a skim. ([Visual Studio Code][1])
* GitHub’s **Chat cookbook** keeps bite-sized prompts for common debugging tasks (invalid JSON, API rate limits, etc.). ([GitHub Docs][5])

If you tell me your editor (VS Code, JetBrains, or Visual Studio) and language, I’ll tailor this to your exact setup and add editor-specific keybindings.

[1]: https://code.visualstudio.com/docs/copilot/guides/debug-with-copilot "Debug with GitHub Copilot"
[2]: https://docs.github.com/en/copilot/reference/cheat-sheet "GitHub Copilot Chat cheat sheet - GitHub Docs"
[3]: https://docs.github.com/en/get-started/learning-to-code/learning-to-debug-with-github-copilot "Learning to debug with GitHub Copilot - GitHub Docs"
[4]: https://docs.github.com/en/copilot/responsible-use/chat-in-your-ide?utm_source=chatgpt.com "Responsible use of GitHub Copilot Chat in your IDE"
[5]: https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook/debug-errors "Debug errors - GitHub Docs"
