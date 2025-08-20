# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Project description: https://raw.githubusercontent.com/florinpop17/app-ideas/refs/heads/master/Projects/3-Advanced/Elevator-App.md (do not use this, it's just doc for developer)

## Project Overview
Simple .NET 8.0 console application that outputs "Hello, World!" - serves as a basic template for C# console applications.

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

### Testing (xUnit recommended)
- **All tests**: `dotnet test`
- **Collect coverage** (with `coverlet.collector`):  
  `dotnet test /p:CollectCoverage=true`
- **Single test** (exact method):  
  `dotnet test --filter "FullyQualifiedName=ElevatorApp.Tests.Unit.MyTests.My_method_should_do_x"`
- **By display name contains**:  
  `dotnet test --filter "DisplayName~should_do_x"`
- **Watch mode** (fast feedback): `dotnet watch test`

## Project Structure

```
HelloConsole/
├── HelloConsole.csproj    # Project file
├── Program.cs             # Main application entry point
├── CLAUDE.md             # Project documentation
├── bin/                  # Build output (generated)
└── obj/                  # Build artifacts (generated)
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

[List of deps]

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

## Implementation Priority
1. Core functionality first (domain logic, state)
2. User interactions / I/O (only minimal working functionality)
3. Minimal, focused unit tests covering the core paths

### Iteration Target
- ~5 minutes per cycle
- Keep tests small and focused on core behavior
- Prioritize working code over perfection for POCs
