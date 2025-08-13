Here’s a refined summary of the Visual Studio Code documentation on **MCP (Model Context Protocol) Servers** and how they integrate with GitHub Copilot Chat—especially in *Agent* mode:

---

## What Are MCP Servers in VS Code?

* **MCP (Model Context Protocol)** is an open standard that lets AI models (like Copilot’s agent mode) discover and invoke external tools—such as APIs, databases, or file systems—through a unified interface. ([Visual Studio Code][1])
* In VS Code, MCP turns your Copilot Chat into a more capable assistant by enabling it to perform actions beyond code suggestions, like interacting with tools, accessing resources, or making HTTP requests. ([DEV Community][2])

---

## How It Works in VS Code

### Architecture

* MCP follows a **client-server model**:

  * **Clients** (like VS Code’s Copilot Chat) connect and send requests.
  * **Servers** provide tools and services the AI model can leverage.
  * Communication happens over standardized transports such as **stdio**, **HTTP**, or **Server-Sent Events (SSE)**. ([Visual Studio Code][1])

### Supported MCP Features

VS Code supports:

* Multiple transport mechanisms: `stdio`, `http`, `sse`.
* Core MCP primitives: *tools*, along with prompts, resources, elicitation, sampling, and authentication. ([Visual Studio Code][1], [Microsoft Learn][3])
* It provides context to the MCP server via `roots` (project folders). ([Visual Studio Code][1])

---

## Finding & Configuring MCP Servers

### Discovery & Installation

* A **curated list** of community and official MCP servers can be found on the VS Code documentation site and installed directly. ([Visual Studio Code][1])
* Alternatively, define servers manually:

  * In **user settings**, to enable MCP across all workspaces.
  * In workspace-level `.vscode/mcp.json` files, for project-specific configurations.
  * Use the **Command Palette** and the **MCP: Show Installed Servers** command to view what’s configured. ([GitHub Docs][4], [Visual Studio Code][1])

### Server Lifecycle

* Upon startup or configuration, VS Code initializes MCP servers by handing them context (`roots`) and querying available tools.
* Tool listings are **cached**—you can reset them using the **MCP: Reset Cached Tools** command. ([Visual Studio Code][1])

---

## Using MCP in Copilot Chat (Agent Mode)

* Switch your Copilot Chat to **Agent** mode to enable MCP tools. ([GitHub Docs][4])
* You’ll see a **tools icon** in the chat UI, showing all available tools. ([GitHub Docs][4])
* You can also define **toolsets**—groupings of related tools—for easier enabling/disabling. ([GitHub Docs][4])
* Interactions follow a permission flow: when Copilot invokes a tool, you get a confirmation prompt (e.g., “Allow” or “Continue”). ([Microsoft Learn][3])
* Use slash commands like `/mcp.servername.promptname` to invoke predefined prompts from servers, or insert resources from MCP directly into chat context. ([GitHub Docs][4])
* If you've initialized MCP in another environment (e.g., Claude Desktop), VS Code can auto-detect it when you enable `"chat.mcp.discovery.enabled": true`. ([GitHub Docs][4])

---

## Recap Table

| Feature                     | VS Code + Copilot Chat (Agent Mode)                                       |
| --------------------------- | ------------------------------------------------------------------------- |
| **What it does**            | Enables AI to use external tools and services via MCP                     |
| **Transports supported**    | `stdio`, `http`, `sse`                                                    |
| **Configuration methods**   | Curated list, `.vscode/mcp.json`, user & workspace settings               |
| **Tool lifecycle handling** | Discovery, caching, UI listing, manual reset                              |
| **Tool invocation**         | Via chat UI—tools icon, prompts, confirmations                            |
| **Advanced usage**          | Toolsets, resources, slash commands, config reuse from other environments |

---

Let me know if you'd like a walkthrough on setting up an MCP server, writing `.mcp.json`, or using specific tools in Agent mode—I can guide step-by-step!

[1]: https://code.visualstudio.com/docs/copilot/chat/mcp-servers?utm_source=chatgpt.com "Use MCP servers in VS Code"
[2]: https://dev.to/shrsv/boost-vs-code-copilot-with-mcp-servers-a-detailed-guide-5fh4?utm_source=chatgpt.com "Boost VS Code Copilot with MCP Servers: A Detailed Guide"
[3]: https://learn.microsoft.com/en-us/visualstudio/ide/mcp-servers?view=vs-2022&utm_source=chatgpt.com "Use MCP servers (Preview) - Visual Studio (Windows)"
[4]: https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp?utm_source=chatgpt.com "Extending Copilot Chat with the Model Context Protocol ..."
