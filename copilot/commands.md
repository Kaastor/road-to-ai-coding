Here’s a compact cheat-sheet of the **most useful GitHub Copilot commands in VS Code** (Command Palette names shown exactly), with what they do and when to reach for them.

> ⚠️ Command names can vary slightly by VS Code/Copilot version. If a command isn’t there, update the Copilot & Copilot Chat extensions and VS Code, or use the fallback noted.

| Command (Command Palette)                           | What it does                                                                                    | Best when to use                                                                                                                                   |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GitHub Copilot: Open Completions Panel**          | Opens a tab showing multiple completion options side-by-side.                                   | You want to compare alternatives or nudge Copilot with a short prompt and pick the best snippet. ([GitHub][1])                                     |
| **GitHub Copilot: Change Completions Model**        | Lets you switch the LLM used for inline suggestions.                                            | Tuning for speed vs. quality (e.g., faster coding vs. deeper reasoning). ([Visual Studio Code][2])                                                 |
| **GitHub Copilot: Manage Language Models**          | Central place to pick/model providers (e.g., Azure/OpenAI/Anthropic where available).           | You need to change provider/model for your org/project. ([GitHub][3])                                                                              |
| **GitHub Copilot: Review and Comment**              | Asks Copilot to review a selected code region and leave inline comments / Problems entries.     | Quick pre-PR review of your changes or focused feedback on one file. ([GitHub Docs][4])                                                            |
| **Chat: Focus on Chat View**                        | Brings focus to Copilot Chat pane.                                                              | You want to prompt Copilot (ask, edit, agent modes) without touching the mouse. ([GitHub][5])                                                      |
| **Chat: Run Prompt**                                | Runs a saved prompt file (from `.github/prompts/`).                                             | Reusing standard prompts for tasks like scaffolding tests, docs, or refactors. ([Visual Studio Code][6])                                           |
| **Chat: Attach Instructions**                       | Attaches a custom instructions file (e.g., `.github/copilot-instructions.md`) to shape answers. | Enforcing project/style rules across all chat interactions. ([Visual Studio Code][6])                                                              |
| **GitHub Copilot: Collect Diagnostics**             | Gathers connectivity + extension diagnostics in an editor tab.                                  | Troubleshooting “Copilot isn’t responding”/network issues; attach to bug reports. ([Visual Studio Code][7])                                        |
| **Output: Show Output Channels** → *GitHub Copilot* | Opens the *Output* panel scoped to Copilot/Copilot Chat logs.                                   | Live-tailing how Copilot is behaving (errors, requests) while you reproduce an issue. ([Visual Studio Code][7])                                    |
| **Developer: Set Log Level** (set to **Trace**)     | Increases VS Code log verbosity (can target Copilot extensions).                                | You need deep logs for tricky/enterprise networking problems. ([Visual Studio Code][7])                                                            |
| **GitHub Copilot: Open Logs** *(if present)*        | Shortcut that jumps straight to Copilot logs.                                                   | When you want logs fast without hunting the right Output channel. If missing, use “Output: Show Output Channels.” ([GitHub][8], [ask.csdn.net][9]) |

### Quick usage tips

* **Comparing completions fast:** Type a function signature, run **GitHub Copilot: Open Completions Panel**, skim options, and insert the winner. ([GitHub][1])
* **Model tuning:** If completions feel off (too short/slow), try **Change Completions Model** or **Manage Language Models** to pick something that fits your task. ([Visual Studio Code][2], [GitHub][3])
* **Lightweight reviews:** Highlight code → **Review and Comment** for actionable inline feedback, before you push or open a PR. ([GitHub Docs][4])
* **Standardize prompting:** Keep reusable prompts and instructions in your repo, then use **Attach Instructions** / **Run Prompt** so teammates get consistent results. ([Visual Studio Code][6])
* **Troubleshooting flow:** **Collect Diagnostics** → check **Output: Show Output Channels (GitHub Copilot)** → optionally raise log level with **Developer: Set Log Level**. ([Visual Studio Code][7])

If you want, tell me your workflow (languages, frameworks, solo vs. team), and I’ll tailor a tiny keybinding set so these sit on easy shortcuts.

[1]: https://github.com/orgs/community/discussions/162320?utm_source=chatgpt.com "How to get Github Copilot Suggestions window in VsCode"
[2]: https://code.visualstudio.com/docs/copilot/ai-powered-suggestions?utm_source=chatgpt.com "Code completions with GitHub Copilot in VS Code"
[3]: https://github.com/microsoft/vscode/issues/260535 "GitHub Copilot: Azure language model provider not showing API key configuration UI · Issue #260535 · microsoft/vscode · GitHub"
[4]: https://docs.github.com/copilot/using-github-copilot/code-review/using-copilot-code-review "Using GitHub Copilot code review - GitHub Docs"
[5]: https://accessibility.github.com/documentation/guide/github-copilot-vsc/?utm_source=chatgpt.com "Using GitHub Copilot in Visual Studio Code with a Screen ..."
[6]: https://code.visualstudio.com/docs/copilot/copilot-customization?utm_source=chatgpt.com "Customize AI responses in VS Code"
[7]: https://code.visualstudio.com/docs/copilot/faq "GitHub Copilot frequently asked questions"
[8]: https://github.com/microsoft/vscode-copilot-release/issues/1484?utm_source=chatgpt.com "WSL: Error Code: ETIMEDOUT · Issue #1484"
[9]: https://ask.csdn.net/questions/8590721?utm_source=chatgpt.com "编程语言- GitHub Copilot 更新后无法自动补全代码"
