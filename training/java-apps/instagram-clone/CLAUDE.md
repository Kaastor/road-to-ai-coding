# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Project description: https://raw.githubusercontent.com/florinpop17/app-ideas/refs/heads/master/Projects/3-Advanced/Elevator-App.md (do not use this, it's just doc for developer)

## Project Overview
A clone of Facebook's Instagram app where you can login/register, create new posts, follow other users and see other people you follows posts

You should create a MVP (Minimum Viable Product) using a Full stack approach such as the MEAN, MERN or VENM Stack to store images to the server and display them to the client.

## User Stories

-   [x] User can register for an account storing their name, email/username and password then login to the app using their credentials
-   [x] User can create a post and store content to the server (text posts implemented, images planned)
-   [ ] User has a profile that displays all the images they have uploaded
-   [ ] User can follow other users
-   [ ] User can see other users posts (people who the user follows)

## Web Application Usage

### Starting the Application
- **Run web server**: `mvn -q exec:java` (starts on http://localhost:8080)
- **Alternative**: `mvn spring-boot:run`
- **Access**: http://localhost:8080 (home page with navigation)
- **API Documentation**: http://localhost:8080/api-docs

### Available Endpoints
- **REST API Base**: `/api/`
  - `POST /api/users/register` - Register new user
  - `POST /api/users/login` - Login user
  - `GET /api/users/me` - Get current user info (requires Session-Id header)
  - `POST /api/users/logout` - Logout user
  - `POST /api/posts` - Create new post (requires authentication)
  - `GET /api/posts/user/{userId}` - Get user's posts
  - `GET /api/posts/my` - Get current user's posts (requires authentication)
- **Web Pages**: `/`, `/register`, `/login`, `/posts`, `/api-docs`

### Quick API Test
```bash
# Register user
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login (save sessionId from response)
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"usernameOrEmail":"testuser","password":"password123"}'

# Create post (use sessionId from login)
curl -X POST http://localhost:8080/api/posts \
  -H "Content-Type: application/json" \
  -H "Session-Id: YOUR_SESSION_ID" \
  -d '{"content":"My first post!"}'
```

## Build & Test Commands

### Using Maven (Java 17)
- Build (skip tests): `mvn -q -DskipTests package`
- Build & run tests: `mvn -q clean verify`
- Compile only: `mvn -q -DskipTests compile`

### Testing (JUnit 5)
- All tests: `mvn -q test`
- Single test class: `mvn -q -Dtest=UserControllerTest test`
- Single test method: `mvn -q -Dtest=UserControllerTest#shouldRegisterUserSuccessfully test`
- Fail fast on first failure: `mvn -q -Dsurefire.failIfNoSpecifiedTests=false -DfailIfNoTests=false test`

> Tip: Prefer the Maven Wrapper if present: `./mvnw …`

## Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           ├── hello/
│   │           │   └── InstagramCli.java
│   │           └── instagram/
│   │               ├── InstagramApp.java (CLI)
│   │               ├── InstagramWebApp.java (Spring Boot Main)
│   │               ├── controller/
│   │               │   ├── UserController.java (REST API)
│   │               │   ├── PostController.java (REST API)
│   │               │   └── WebController.java (HTML pages)
│   │               ├── model/
│   │               │   ├── User.java
│   │               │   └── Post.java
│   │               ├── repository/
│   │               │   ├── UserRepository.java
│   │               │   ├── InMemoryUserRepository.java
│   │               │   ├── PostRepository.java
│   │               │   └── InMemoryPostRepository.java
│   │               └── service/
│   │                   ├── AuthenticationService.java
│   │                   ├── UserService.java
│   │                   └── PostService.java
│   └── resources/
│       └── templates/ (Thymeleaf HTML templates)
│           ├── index.html
│           ├── register.html
│           ├── login.html
│           ├── posts.html
│           └── api-docs.html
└── test/
    └── java/
        └── com/
            └── example/
                ├── hello/
                │   └── InstagramCliTest.java
                └── instagram/
                    ├── InstagramWebAppTest.java (Spring Boot test)
                    ├── controller/
                    │   └── UserControllerTest.java (Web layer test)
                    ├── model/
                    │   ├── UserTest.java
                    │   └── PostTest.java
                    ├── repository/
                    │   ├── UserRepositoryTest.java
                    │   └── PostRepositoryTest.java
                    └── service/
                        ├── AuthenticationServiceTest.java
                        ├── UserServiceTest.java
                        └── PostServiceTest.java
pom.xml
CLAUDE.md
README.md
target/
```

## Technical Stack

- **Java version**: Java 17 (LTS)
- **Build tool**: Maven (use Maven Wrapper if available)
- **Web framework**: Spring Boot 3.2.0 with embedded Tomcat
- **Template engine**: Thymeleaf for HTML rendering
- **Testing**: JUnit 5 (Jupiter) + Maven Surefire + Spring Boot Test
- **Logging**: SLF4J API with Logback (or JUL bridge) for runtime logs
- **Static analysis** (optional but recommended): Checkstyle/Spotless, PMD, SpotBugs

### Dependencies

Keep production and test dependencies separated in `pom.xml` using appropriate scopes:
- **Web**: `spring-boot-starter-web` (REST API, embedded Tomcat), `spring-boot-starter-thymeleaf` (HTML templates)
- **Test**: `spring-boot-starter-test`, `org.junit.jupiter:junit-jupiter`, `org.mockito:mockito-core`
- **Main**: Built-in Spring Boot logging (Logback)

> Ensure Surefire is configured for JUnit 5 (Maven Surefire 2.22+ auto-detects Jupiter).

## Code Style Guidelines

- **Style**: Google Java Style (or project’s chosen Checkstyle). Prefer automated formatting (e.g., Spotless/Google Java Format).
- **Documentation**: Javadoc on public classes/methods; concise KDocs on internal APIs as needed.
- **Naming**:
  - Classes/Interfaces/Enums/Records: `PascalCase`
  - Methods/Fields/Variables/Packages: `lowerCamelCase` (packages all lowercase)
  - Constants: `UPPER_SNAKE_CASE`
- **Method length**: Keep methods short (< 30 lines) and single-purpose.
- **Immutability**: Prefer immutable value types; use `record` for simple data carriers.
- **Nullability**: Avoid returning `null`; use `Optional` when absence is valid. Validate inputs with `Objects.requireNonNull`.
- **Formatting**: No wildcard imports; one top-level type per file.

## Java Best Practices

- **I/O**: Use NIO.2 (`java.nio.file.Path`, `Files`) and try-with-resources for all closables.
- **Time**: Use `java.time` (e.g., `Instant`, `Duration`, `LocalDateTime`) — avoid legacy `Date/Calendar`.
- **Collections**: Prefer interfaces (`List`, `Map`) and unmodifiable views (`List.copyOf`, `Collections.unmodifiableList`).
- **Logging**: Use SLF4J (`logger.info("Moved to floor {}", floor)`) — never `System.out.println` in production code.
- **Error handling**: Throw specific exceptions with context. Don’t swallow exceptions; either handle or wrap and rethrow.
- **Concurrency**: Use `ExecutorService`, `CompletableFuture`, and structured locking; avoid synchronized blocks on `this`.
- **Configuration**: Read from environment variables or properties files; keep secrets out of VCS.
- **API design**: Keep methods cohesive, avoid boolean parameter flags; prefer small, composable classes.

## Development Patterns & Best Practices

- **Favor simplicity**: Choose the simplest solution that meets requirements.
- **DRY principle**: Reuse functionality; extract helpers where duplication appears.
- **Configuration management**: Profile-specific props in `src/main/resources`; override with env vars when deploying.
- **Focused changes**: Implement only explicitly requested or well-understood changes.
- **File size**: Keep files under ~300 lines; refactor when exceeding this limit.
- **Test coverage**: Aim for meaningful unit & integration tests; measure with JaCoCo if configured.
- **Test structure**: Prefer parameterized tests (`@ParameterizedTest` with `@CsvSource`/`@MethodSource`) for table-driven scenarios.
- **Mocking**: Use Mockito for external dependencies; avoid mocking value objects. Focus on behavior and public API.
- **Modular design**: Small, cohesive classes; depend on interfaces where appropriate.
- **Logging levels**: Use `debug` for diagnostics, `info` for key milestones, `warn/error` for issues with context.
- **Performance**: Optimize hot paths only after measuring (JMH for microbenchmarks if needed).

## Testing Conventions

- **Naming**: `*Test` for unit tests, `*IT` for integration tests (use Failsafe plugin if integration tests are added).
- **Given/When/Then**: Structure tests for readability.
- **Assertions**: Prefer expressive assertions (AssertJ) for readability; otherwise JUnit’s `Assertions`.
- **Parameterization**: Use `@ParameterizedTest` for matrix-like inputs.
- **Fixtures**: Keep setup minimal; use factory methods/builders for test data.
- **Determinism**: Avoid time/thread randomness; use fakes and fixed clocks.

## Core Workflow
- Compile to type-check after changes: `mvn -q -DskipTests compile`
- Prefer running single tests over the whole suite for speed during development
- Keep feedback loops tight; commit small, coherent changes

## Implementation Priority
1. Core functionality first (state transitions, rendering/printing output)
2. User interactions
   - Implement only minimal working functionality
3. Minimal unit tests

### Iteration Target
- Around 5 min per cycle
- Keep tests simple, just core functionality checks
- Prioritize working code over perfection for POCs

## Implementation Plan (Compact)

### Phase 1: Foundation & User Management (6 iterations)
- **1.1:** Domain Models & Project Structure - User record, package structure, tests
- **1.2:** User Repository Layer - CRUD interface, in-memory storage, tests  
- **1.3:** User Service Layer - Registration logic, validation, business rules
- **1.4:** Authentication System - Login/logout, session management, credential validation
- **1.5:** CLI User Interface - Main class, registration/login commands, menu system
- **1.6:** Integration Testing - Full user flow testing, end-to-end verification

### Phase 2: Basic Post Management (5 iterations)
- **2.1:** Post Domain Model - Post record, validation, creation logic
- **2.2:** Post Repository - CRUD operations, user association, storage
- **2.3:** Post Service - Business logic, content validation, user checks
- **2.4:** CLI Post Features - Create/view commands, listing, timestamps
- **2.5:** Post Integration Testing - Full post workflow verification

### Phase 3: Image Handling & Storage (4 iterations)
- **3.1:** Image Storage Foundation - ImageService interface, filesystem storage
- **3.2:** Image Upload Simulation - CLI upload, path storage, validation
- **3.3:** Image Display in CLI - Path display, metadata, details command
- **3.4:** Image Integration Testing - Complete image workflow verification

### Phase 4: Social Features (5 iterations)
- **4.1:** Following Domain Model - Follow record, repository, operations
- **4.2:** Follow Service Layer - Business logic, validation, relationship methods
- **4.3:** CLI Social Features - Follow/unfollow commands, user search
- **4.4:** User Profile Enhancement - Follower counts, profile views, stats
- **4.5:** Social Integration Testing - Complete social workflow verification

### Phase 5: Feed Generation & Advanced Features (4 iterations)
- **5.1:** Feed Service - Personalized feeds, chronological ordering, generation logic
- **5.2:** CLI Feed Interface - Feed display, author info, timestamps
- **5.3:** Enhanced Feed Features - Pagination, user posts, activity indicators
- **5.4:** Final Integration & Polish - Complete user journey testing, bug fixes

## Frontend Implementation Plan (Compact)

Phase 1: Web Foundation (2-3 iterations)
  - Add Spring Boot web dependencies and configure web
   server
  - Create REST controllers for existing services

  Phase 2: Basic Web Interface (3-4 iterations)
  - Create HTML templates and forms for user
  registration/login/posts
  - Add basic CSS styling and navigation

  Phase 3: Testing & Polish (1-2 iterations)
  - End-to-end testing and error handling
  - Final integration verification

  Technical Stack: Spring Boot + Thymeleaf + existing
  service layer + in-memory storage