# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
[Brief description of what this project does and its main purpose]

[Optional: MVP/Phase approach if project is being built incrementally]

## User Stories / Requirements

-   [ ] [Key user requirement 1]
-   [ ] [Key user requirement 2]
-   [ ] [Key user requirement 3]

## Bonus features / Future Enhancements

-   [ ] [Optional feature 1]
-   [ ] [Optional feature 2]
-   [ ] [Optional feature 3]

## Technical Stack

- **.NET SDK**: **8.0** (verify with `dotnet --version`)
- **Language**: **C# 12**
- **Project type**: [Console/Web/Library/etc.]
- **Package management**: **NuGet** (`PackageReference` in `.csproj`)
- **Testing**: **xUnit** + **FluentAssertions**

## Project Structure

```
{ProjectName}/
├── {ProjectName}.csproj     # Main project file
├── Program.cs               # Application entry point
├── Models/                  # Domain models (if applicable)
├── Services/                # Business logic (if applicable)
├── Controllers/             # Web controllers (web projects only)
├── Views/                   # Razor views (web projects only)
├── wwwroot/                 # Static files (web projects only)
├── tests/                   # Test projects directory
│   └── {ProjectName}.Tests/ # Main test project
│       ├── {ProjectName}.Tests.csproj
│       ├── Models/          # Model tests (if applicable)
│       ├── Services/        # Service tests (if applicable)
│       └── Controllers/     # Controller tests (if applicable)
├── bin/                     # Build output (generated)
├── obj/                     # Build artifacts (generated)
└── CLAUDE.md               # Project documentation
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
<!-- Add to main {ProjectName}.csproj -->
<ItemGroup>
  <Compile Remove="tests/**/*" />
</ItemGroup>
```

**Test project dependencies** (`tests/{ProjectName}.Tests/{ProjectName}.Tests.csproj`):
```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
  <PackageReference Include="xunit" Version="2.6.1" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
  <PackageReference Include="FluentAssertions" Version="6.12.0" />
  <PackageReference Include="coverlet.collector" Version="6.0.0" />
  
  <!-- Add for web projects -->
  <!-- <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.0" /> -->
</ItemGroup>

<ItemGroup>
  <ProjectReference Include="../../{ProjectName}.csproj" />
</ItemGroup>
```

**Why**: .NET SDK automatically includes all `.cs` files. Test files have different dependencies (xUnit, FluentAssertions) unavailable to the main project, causing build failures.

## Implementation Plan
[Plan]

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
- **Structure**: Unit tests in `tests/{ProjectName}.Tests`
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
[Optional: Delete this section if not relevant to your project type]

- **Fail Fast**: Detect problematic scenarios early and exit gracefully
- **User Feedback**: Clear messages explaining why the application is exiting
- **Resource Cleanup**: Proper disposal and cancellation token usage
- **Defensive Programming**: Assume input can be malformed or missing

## Project-Specific Notes
[Optional: Add any project-specific configuration, constraints, or requirements here]

<!-- Template Usage Instructions:
1. Replace all {ProjectName} placeholders with your actual project name
2. Fill in the Project Overview section with your project description
3. Update User Stories/Requirements with your actual requirements
4. Modify Technical Stack section to match your specific technology choices
5. Adjust Project Structure to match your actual folder organization
6. Update Implementation Plan if using phased development approach
7. Add any project-specific notes in the final section
8. Delete optional sections marked with [Optional: ...] if not needed
9. Delete these template instructions before using
-->