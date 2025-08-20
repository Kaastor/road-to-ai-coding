# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Real-time chat interface where multiple users can interact with each other by sending messages.

**Current Status**: Console-based MVP with message storage completed (Phases 1-2). Ready for web interface implementation (Phase 3).

As a MVP(Minimum Viable Product) you can focus on building the Chat interface. Real-time functionality can be added later (the bonus features).

## User Stories / Requirements

-   [x] User is prompted to enter a username when he visits the chat app. The username will be stored in the application
-   [x] User can see an `input field` where he can type a new message (console-based)
-   [x] By pressing the `enter` key the text will be displayed in the `chat` alongside his username (e.g. `John Doe: Hello World!`)

## Bonus features / Future Enhancements

-   [ ] The messages will be visible to all the Users that are in the chat app (using WebSockets)
-   [ ] When a new User joins the chat, a message is displayed to all the existing Users
-   [ ] Messages are saved in a database
-   [ ] User can send images, videos and links which will be displayed properly
-   [ ] User can select and send an emoji
-   [ ] Users can chat in private
-   [ ] Users can join `channels` on specific topics

## Technical Stack

- **.NET SDK**: **8.0.413** (verified)
- **Language**: **C# 12**
- **Project type**: Console Application (Phase 1-2 complete, Web planned for Phase 3+)
- **Package management**: **NuGet** (`PackageReference` in `.csproj`)
- **Testing**: **xUnit** + **FluentAssertions**

## Project Structure

```
ChatApp/
├── ChatApp.csproj        # Main project file
├── Program.cs            # Main application entry point
├── Directory.Build.props # Build configuration
├── Models/               # Domain models
│   └── Message.cs        # Message record class
├── Services/             # Business logic
│   ├── IChatService.cs   # Chat service interface
│   └── InMemoryChatService.cs # In-memory implementation
├── Controllers/          # Web controllers (Phase 3+ - not implemented)
├── Views/                # Razor views (Phase 3+ - not implemented)
├── wwwroot/              # Static files (Phase 3+ - not implemented)
├── tests/                # Test projects directory
│   └── ChatApp.Tests/    # Main test project
│       ├── ChatApp.Tests.csproj
│       ├── Models/       # Model tests
│       │   └── MessageTests.cs
│       └── Services/     # Service tests
│           └── InMemoryChatServiceTests.cs
├── bin/                  # Build output (generated)
├── obj/                  # Build artifacts (generated)
├── packages.lock.json    # NuGet lock file
└── CLAUDE.md            # Project documentation
```

## Build & Test Commands

### Essential Commands
```bash
# Initial setup
dotnet restore                    # First time only

# Fast development (recommended)
dotnet watch run                  # Auto-rebuild + rerun on file changes
dotnet watch test                 # Auto-rerun tests on changes

# Manual commands
dotnet build                      # Build project
dotnet test                       # Run all tests
dotnet run                        # Run application
dotnet format                     # Format code
```

### Performance Optimizations
```bash
# Skip operations when unchanged
dotnet build --no-restore        # Skip restore if packages unchanged
dotnet test --no-build           # Skip build if already built
dotnet build -m                  # Parallel build (use all CPU cores)

# Targeted testing
dotnet test --filter "DisplayName~should_do_x"    # Filter tests by name
dotnet test /p:CollectCoverage=true              # Collect coverage
```

## Test Project Configuration

**IMPORTANT**: Main project must exclude test files to prevent build conflicts:

```xml
<!-- Add to main ChatApp.csproj -->
<ItemGroup>
  <Compile Remove="tests/**/*" />
</ItemGroup>
```

**Test project dependencies** (`tests/ChatApp.Tests/ChatApp.Tests.csproj`):
```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
  <PackageReference Include="xunit" Version="2.5.3" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
  <PackageReference Include="FluentAssertions" Version="6.12.0" />
  <PackageReference Include="coverlet.collector" Version="6.0.0" />
</ItemGroup>

<ItemGroup>
  <ProjectReference Include="../../ChatApp.csproj" />
</ItemGroup>

<ItemGroup>
  <Using Include="Xunit" />
</ItemGroup>
```

**Why**: .NET SDK automatically includes all `.cs` files. Test files have different dependencies (xUnit, FluentAssertions) unavailable to the main project, causing build failures.

## Implementation Plan - Modular PoC Approach

### Phase 1: Basic Console Chat Setup ✅
- Create basic console app structure
- Implement username collection on startup  
- Basic message input/output loop
- Infinite loop protection with robust guards

### Phase 2: Message Storage & Display ✅
- Create `Message` record class
- Implement `IChatService` interface  
- Add in-memory message storage
- Format messages as "Username: Message"

### Phase 3: Web Interface Foundation
- Set up ASP.NET Core web application
- Create basic controller and views
- Username prompt page/modal
- Chat message display area

### Phase 4: Interactive Functionality  
- Form submission for messages
- Enter key support (JavaScript)
- Send button functionality
- Session-based username storage

### Current Implementation Status
- **Phase 1**: ✅ **Complete** - Console application with username input, message loop, error handling
- **Phase 2**: ✅ **Complete** - Message model, IChatService interface, InMemoryChatService implementation
- **Phase 3**: ⏳ **Pending** - Web interface foundation (not yet implemented)
- **Phase 4**: ⏳ **Pending** - Interactive web functionality (not yet implemented)

### Architecture Overview
- **Domain**: `Message` record class with Username, Content, Timestamp
- **Service**: `IChatService` interface with `InMemoryChatService` implementation  
- **Console**: Robust console application with cancellation, timeout, and error handling
- **Web**: Single controller with 2-3 views (Phase 3+ - not implemented)
- **Storage**: In-memory list (no database for PoC)
- **Testing**: Complete unit tests for models and services

## Code Style Guidelines

- **Naming**:
  - **PascalCase**: classes, records, structs, enums, methods, public properties
  - **camelCase**: local variables & parameters
  - **_camelCase**: private fields (prefer `readonly`)
  - **I** prefix for interfaces (e.g., `IService`)
- **Files**: Prefer **file-scoped namespaces**; one public type per file
- **Nullability**: `<Nullable>enable</Nullable>` in all projects
- **Async**: Use `async/await`, return `Task`/`Task<T>`; suffix async methods with `Async`
- **Function length**: Keep methods focused and short (≈ ≤ 30 lines)
- **Formatting**: Enforced via `.editorconfig` + `dotnet format`

## C# / .NET Best Practices

- **Collections & immutability**: Prefer `IReadOnlyList<T>`, `IReadOnlyDictionary<K,V>` and immutable patterns; use `record` for DTOs/value objects
- **LINQ**: Use when it improves clarity; avoid extra allocations in hot paths
- **Pattern matching**: Use `switch` expressions & property patterns for clarity
- **Guard clauses**: `ArgumentNullException.ThrowIfNull(arg, nameof(arg));`
- **IDisposable**: Use `using`/`await using` blocks; prefer dependency injection for lifetimes
- **Logging**: Use `Microsoft.Extensions.Logging.ILogger<T>`; structured logs
- **Error handling**: Throw specific exceptions; catch narrowly; include context in messages
- **Concurrency**: Prefer `async` APIs; avoid blocking (`.Result`, `.Wait()`); use `CancellationToken`
- **Security**:
  - Validate all inputs
  - Never log secrets or PII  
  - Store secrets in user-secrets/env/secret manager (not in repo)

## Development Patterns & Best Practices

- **Favor simplicity**: Ship the simplest solution that meets requirements
- **DRY**: Extract reusable components; keep helpers internal
- **Preserve patterns**: Follow existing architecture & naming when patching
- **File size**: Keep files under ~300 lines; refactor once they grow past that
- **Modular design**: Small, testable services/components; depend on abstractions
- **Dependency Injection**: Use built-in DI; prefer constructor injection

## Testing Strategy

- **Framework**: **xUnit** + **FluentAssertions**
- **Mocking**: **Moq** or **NSubstitute**; mock external dependencies only
- **Structure**: Unit tests in `tests/ChatApp.Tests`
- **Naming**: `MethodName_Should_ExpectedBehavior_When_Condition`
- **Parameterized**: Use `[Theory]` with `[InlineData]` / `[MemberData]`
- **Integration tests**: For ASP.NET Core use `WebApplicationFactory<TEntryPoint>`
- **Don'ts**: Don't assert private implementation details; verify observable behavior

## Core Workflow
- After changes: `dotnet build` (no warnings), `dotnet test` (targeted tests)
- Prefer running **single tests** with `--filter` for speed during iteration
- Run `dotnet format` before committing
- Use **watch mode** (`dotnet watch run/test`) to eliminate manual build/run cycles

## Error Handling Philosophy

- **Fail Fast**: Detect problematic scenarios early and exit gracefully
- **User Feedback**: Clear messages explaining why the application is exiting
- **Resource Cleanup**: Proper disposal and cancellation token usage
- **Defensive Programming**: Assume input can be malformed or missing

## Current Implementation Details

### Console Application Features
- **Username Input**: Validates non-empty usernames with retry logic (max 5 attempts)
- **Message Loop**: Interactive chat with `username: message` format
- **Exit Command**: Type 'exit' to quit gracefully
- **Error Handling**: 
  - Piped input detection and graceful exit
  - Empty input protection (exits after 10 consecutive empty inputs)
  - Timeout handling (30-second input timeout)
  - Ctrl+C cancellation support

### Domain Models
- **Message**: Record class with Username, Content, and UTC Timestamp
- **IChatService**: Interface with AddMessage, GetMessages, GetRecentMessages
- **InMemoryChatService**: Thread-safe implementation with validation

### Testing Coverage
- **Unit Tests**: Complete coverage for Message model and InMemoryChatService
- **Edge Cases**: Input validation, null handling, boundary conditions
- **Test Framework**: xUnit with FluentAssertions for readable assertions

## Testing Scenarios Covered

- **Piped Input**: `echo "test" | dotnet run` → Graceful exit with warning
- **Empty Input Loops**: Consecutive empty inputs → Exit after 10 attempts  
- **Failed Username**: Invalid username attempts → Exit after 5 attempts
- **Hanging Input**: No user input → Timeout after 30 seconds
- **User Interruption**: Ctrl+C → Clean cancellation and exit