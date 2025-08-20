# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Project description: https://raw.githubusercontent.com/florinpop17/app-ideas/refs/heads/master/Projects/3-Advanced/Elevator-App.md (do not use this, it's just doc for developer)

## Project Overview
Real-time chat interface where multiple users can interact with each other by sending messages.

As a MVP(Minimum Viable Product) you can focus on building the Chat interface. Real-time functionality can be added later (the bonus features).

## User Stories

-   [ ] User is prompted to enter a username when he visits the chat app. The username will be stored in the application
-   [ ] User can see an `input field` where he can type a new message
-   [ ] By pressing the `enter` key or by clicking on the `send` button the text will be displayed in the `chat box` alongside his username (e.g. `John Doe: Hello World!`)

## Bonus features

-   [ ] The messages will be visible to all the Users that are in the chat app (using WebSockets)
-   [ ] When a new User joins the chat, a message is displayed to all the existing Users
-   [ ] Messages are saved in a database
-   [ ] User can send images, videos and links which will be displayed properly
-   [ ] User can select and send an emoji
-   [ ] Users can chat in private
-   [ ] Users can join `channels` on specific topics

## Build & Test Commands

### Prerequisites
- .NET SDK **8.0** installed (verify with `dotnet --version`)
- (Optional) `global.json` at the repo root to pin SDK 8.0

### Restore & Build
- Restore packages: `dotnet restore`
- Build (debug): `dotnet build`
- Build (release): `dotnet build -c Release`
- Run application: `dotnet run`
- Format code: `dotnet format`

### ⚡ Fast Development Commands (Use These!)
- **Incremental build only**: `dotnet build --no-restore` (skip restore if packages unchanged)
- **Run without build**: `dotnet run --no-build` (if already built)
- **Watch mode (auto-rebuild/rerun)**: `dotnet watch run` ⭐ **Best for dev**
- **Hot reload console**: `dotnet watch run --no-hot-reload` (faster startup)
- **Parallel build**: `dotnet build -m` (use all CPU cores)
- **Skip up-to-date check**: `dotnet build --no-dependencies`

### Testing (xUnit recommended)
- **All tests**: `dotnet test`
- **Collect coverage** (with `coverlet.collector`):  
  `dotnet test /p:CollectCoverage=true`
- **Single test** (exact method):  
  `dotnet test --filter "FullyQualifiedName=ElevatorApp.Tests.Unit.MyTests.My_method_should_do_x"`
- **By display name contains**:  
  `dotnet test --filter "DisplayName~should_do_x"`

### ⚡ Fast Testing Commands
- **Watch mode (auto-rerun)**: `dotnet watch test` ⭐ **Best for TDD**
- **Skip build if unchanged**: `dotnet test --no-build`
- **Skip restore**: `dotnet test --no-restore`
- **Parallel test execution**: `dotnet test --parallel`
- **Fast failing tests only**: `dotnet test --filter "Priority=1"`

## Implementation Plan - Modular PoC Approach

### Phase 1: Basic Console Chat Setup ✅
**Goal**: Establish project foundation
- Create basic console app structure
- Implement username collection on startup
- Basic message input/output loop
- **Infinite Loop Protection**: Implemented robust guards against common scenarios
- **Dependencies**: None (basic .NET 8.0 only)

### Phase 2: Message Storage & Display
**Goal**: Core chat logic
- Create `Message` record class
- Implement `IChatService` interface
- Add in-memory message storage
- Format messages as "Username: Message"

### Phase 3: Web Interface Foundation
**Goal**: Move to web-based UI
- Set up ASP.NET Core web application
- Create basic controller and views
- **Dependencies**: `Microsoft.AspNetCore.Mvc` (built-in)

### Phase 4: Chat UI Components
**Goal**: Build chat interface
- Username prompt page/modal
- Message input field
- Chat message display area
- Basic styling

### Phase 5: Message Handling
**Goal**: Interactive functionality
- Form submission for messages
- Enter key support (JavaScript)
- Send button functionality
- Session-based username storage

### Phase 6: Basic Testing 
**Goal**: Quality assurance
- Unit tests for `ChatService`
- Basic controller tests

### Architecture Overview
- **Domain**: `Message` record, `IChatService` interface
- **Service**: `InMemoryChatService` implementation  
- **Web**: Single controller with 2-3 views
- **Storage**: In-memory list (no database for PoC)

## Project Structure

```
ChatApp/
├── ChatApp.csproj        # Project file
├── Program.cs            # Main application entry point
├── Models/               # Domain models
│   └── Message.cs
├── Services/             # Business logic
│   ├── IChatService.cs
│   └── InMemoryChatService.cs
├── Controllers/          # Web controllers
│   └── ChatController.cs
├── Views/                # Razor views
│   ├── Chat/
│   └── Shared/
├── wwwroot/              # Static files (CSS, JS)
├── CLAUDE.md            # Project documentation
├── bin/                 # Build output (generated)
└── obj/                 # Build artifacts (generated)
```

## Technical Stack

- **.NET SDK**: **8.0**
- **Language**: **C# 12**
- **Project config**: `.csproj` (+ `Directory.Build.props` for shared settings)
- **Environment**:
  - Development secrets: `dotnet user-secrets` (for non-production)
  - Configuration via `appsettings*.json` + environment variables
- **Package management**: **NuGet** (`PackageReference` in `.csproj`)
- **Dependencies**:
  - Runtime deps in `src/*/*.csproj`
  - Dev-only (analyzers, test libs) marked with `<PrivateAssets>all</PrivateAssets>`
- **Project layout**: `src/` for product code, `tests/` for test projects

### Dependencies

**Minimal PoC Dependencies:**
```xml
<!-- Core web functionality (built-in) -->
<PackageReference Include="Microsoft.AspNetCore.Mvc" />

<!-- Testing dependencies -->
<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
<PackageReference Include="xunit" Version="2.6.1" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
<PackageReference Include="FluentAssertions" Version="6.12.0" />
<PackageReference Include="coverlet.collector" Version="6.0.0" />
```

## Code Style Guidelines

- **Naming**:
  - **PascalCase**: classes, records, structs, enums, methods, public properties
  - **camelCase**: local variables & parameters
  - **_camelCase**: private fields (prefer `readonly` where possible)
  - **I** prefix for interfaces (e.g., `IService`)
- **Docs**: XML doc comments `///` for public APIs; keep summaries concise
- **Files**: Prefer **file-scoped namespaces**; one public type per file
- **Nullability**: `<Nullable>enable</Nullable>` in all projects; no `#nullable disable`
- **Async**: Use `async/await`, return `Task`/`Task<T>`; suffix async methods with `Async`
- **Function length**: Keep methods focused and short (≈ ≤ 30 lines)
- **Formatting**: Enforced via `.editorconfig` + `dotnet format`
- **Analyzers**:
  - Enable built-in: `<EnableNETAnalyzers>true</EnableNETAnalyzers>`
  - `<AnalysisLevel>latest</AnalysisLevel>`
  - Consider `StyleCop.Analyzers` for stricter style rules
- **Warnings**: Treat as errors in CI: `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`

## C# / .NET Best Practices

- **Collections & immutability**: Prefer `IReadOnlyList<T>`, `IReadOnlyDictionary<K,V>` and immutable patterns; use `record` for DTOs/value objects
- **LINQ**: Use when it improves clarity; avoid extra allocations in hot paths
- **Pattern matching**: Use `switch` expressions & property patterns for clarity
- **Guard clauses**: `ArgumentNullException.ThrowIfNull(arg, nameof(arg));`
- **IDisposable**: Use `using`/`await using` blocks; prefer dependency injection for lifetimes
- **Logging**: Use `Microsoft.Extensions.Logging.ILogger<T>`; structured logs (`logger.LogInformation("Processed {Count}", count);`)
- **Configuration**: Bind strongly-typed options with validation:
  - `services.AddOptions<MyOptions>().Bind(config.GetSection("My")).ValidateDataAnnotations().ValidateOnStart();`
- **Error handling**: Throw specific exceptions; catch narrowly; include context in messages
- **Concurrency**: Prefer `async` APIs; avoid blocking (`.Result`, `.Wait()`); use `CancellationToken`
- **Security**:
  - Validate all inputs
  - Never log secrets or PII
  - Store secrets in user-secrets/env/secret manager (not in repo)
- **Performance** (when needed): minimize allocations, use `Span<T>`/`Memory<T>` carefully, pool where it matters

## Development Patterns & Best Practices

- **Favor simplicity**: Ship the simplest solution that meets requirements
- **DRY**: Extract reusable components; keep helpers internal
- **Preserve patterns**: Follow existing architecture & naming when patching
- **File size**: Keep files under ~300 lines; refactor once they grow past that
- **Modular design**: Small, testable services/components; depend on abstractions
- **Dependency Injection**: Use built-in DI; prefer constructor injection
- **Logging**: Reasonable log levels (Debug/Information/Warn/Error); no noisy loops
- **Configuration**: Hierarchy = `appsettings.json` < `appsettings.{Environment}.json` < Environment Variables < User Secrets (dev)

## Testing Strategy

- **Framework**: **xUnit**
- **Assertions**: Prefer **FluentAssertions** for readability
- **Mocking**: **Moq** or **NSubstitute**; mock external dependencies only
- **Structure**:
  - Unit tests in `tests/ProjectName.Tests`
  - Naming: `MethodName_Should_ExpectedBehavior_When_Condition`
- **Parameterized (“table-driven”)**:
  - Use `[Theory]` with `[InlineData]` / `[MemberData]`
- **Integration tests**:
  - For ASP.NET Core: `WebApplicationFactory<TEntryPoint>`
  - Use test containers/in-memory providers where applicable
- **Coverage**:
  - Add `coverlet.collector` to test project
  - Run: `dotnet test /p:CollectCoverage=true`
- **Don’ts**: Don’t assert private implementation details; verify observable behavior

## Core Workflow
- After a set of changes: `dotnet build` (no warnings), `dotnet test` (targeted tests)
- Prefer running **single tests** with `--filter` for speed during iteration
- Run `dotnet format` before committing

## ⚡ Optimized Development Workflow

### Initial Setup (Once)
```bash
dotnet restore                    # First time only
```

### Fast Development Cycle (Use These!)
```bash
# Method 1: Watch Mode (RECOMMENDED - fully automated)
dotnet watch run                  # Auto-rebuild + rerun on file changes
# OR for testing:
dotnet watch test                 # Auto-rerun tests on changes

# Method 2: Manual Fast Commands (when watch mode not suitable)
dotnet build --no-restore        # Build only (skip restore)
dotnet run --no-build            # Run without rebuilding
dotnet test --no-build           # Test without rebuilding
```

### Performance Tips
- **Use watch mode**: `dotnet watch run` eliminates manual build/run cycles
- **Skip restore**: Add `--no-restore` when packages haven't changed
- **Skip build**: Add `--no-build` when code hasn't changed
- **Parallel builds**: Add `-m` for multi-core compilation
- **Target specific**: Use `--filter` for single test execution

### Project Configuration Benefits
- **Shared compilation**: Reuses compiler process across builds (faster)
- **Parallel builds**: Uses all CPU cores automatically
- **Incremental restore**: Skips unchanged packages
- **Debug optimizations**: Faster debug builds, slower runtime

## Implementation Priority
1. Core functionality first (domain logic, state)
2. User interactions / I/O (only minimal working functionality)
3. Minimal, focused unit tests covering the core paths

### Iteration Target
- ~5 minutes per cycle
- Keep tests small and focused on core behavior
- Prioritize working code over perfection for POCs

### Testing Scenarios Covered

- **Piped Input**: `echo "test" | dotnet run` → Graceful exit with warning
- **Empty Input Loops**: Consecutive empty inputs → Exit after 10 attempts  
- **Failed Username**: Invalid username attempts → Exit after 5 attempts
- **Hanging Input**: No user input → Timeout after 30 seconds
- **User Interruption**: Ctrl+C → Clean cancellation and exit

### Error Handling Philosophy

- **Fail Fast**: Detect problematic scenarios early and exit gracefully
- **User Feedback**: Clear messages explaining why the application is exiting
- **Resource Cleanup**: Proper disposal and cancellation token usage
- **Defensive Programming**: Assume input can be malformed or missing
