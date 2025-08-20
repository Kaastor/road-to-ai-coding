# Software Development Startup Guide
## Getting Started with Claude Code & TDD

### 🚀 Day 1: Project Initialization

#### Step 2: Create Your claude.md File
Create a file named `claude.md` in your project root with this initial template:

#### Step 3: Use Claude Code to Generate Project Structure
Run your first Claude Code command:
```bash
claude "Generate a project structure for my project with the following requirements:
- Testing setup
- Basic folder structure following best practices
- Configuration files for testing
- A simple README.md
- Package/dependency management setup"
```

### 🏗️ Day 3: First Feature Development

Break down user stories into small steps

#### Step 5: Plan Your First Feature
Update your claude.md file:
```markdown
## Current Context
**Working on:** User Story #1 - [Description]
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
**Next step:** Write E2E test for the feature
```

---

### 🔄 Ongoing Development Workflow

#### Daily Development Cycle

**Morning Setup (5 minutes):**
1. Update claude.md with current context
2. Review yesterday's progress
3. Plan today's tasks

**Development Loop (per feature):**
```bash
# 1. Write the test
claude "Write a test for [specific behavior]"

# 2. Run and watch it fail
[test command]

# 3. Implement minimal solution
claude "Implement code to pass this test: [test code]"

# 4. Run tests again
[test command]

# 5. Refactor if needed
claude "Refactor this code for better [performance/readability]: [code]"

# 6. Commit when green
git add . && git commit -m "type: description"
```

**End of Day (10 minutes):**
1. Run full test suite
2. Update claude.md with progress
3. Document any decisions or patterns discovered
4. Push to remote repository

---

### 🛠️ Essential Claude Code Commands

#### Testing Commands
```bash
# Generate comprehensive test cases
claude "Generate edge case tests for [function/component]"

# Create test fixtures
claude "Create test fixtures for [data structure/model]"

# Analyze test coverage
claude "What test cases are missing for this code: [code]"
```

#### Development Commands
```bash
# Code generation with tests
claude "Create a [component] with corresponding unit tests"

# Refactoring
claude "Refactor this code using [pattern]: [code]"

# Code review
claude "Review this code for issues and improvements: [code]"

claude "Develop a following user story with minimal unit tests: "
```

#### Documentation Commands
```bash
# Generate documentation
claude "Generate documentation for this module: [code]"

# Create examples
claude "Create usage examples for this API: [code]"
```

---

### 📊 Progress Tracking

#### Update claude.md Weekly With:
```markdown
## Week [N] Summary
**Completed:**
- Feature X with N tests
- Refactored Y component
- Coverage: XX%

**Learned:**
- [Key learning or pattern discovered]

**Next Week Focus:**
- [Primary goal]
```

---

### 🚨 Quick Troubleshooting

#### Problem: Tests are slow
```bash
claude "Optimize these slow tests using mocks: [test code]"
```

#### Problem: Unclear how to test something
```bash
claude "What's the best testing strategy for [complex scenario]?"
```

#### Problem: Too much test duplication
```bash
claude "Create test helpers to reduce duplication in: [test files]"
```

#### Problem: Lost context in Claude Code
```bash
# Provide context from claude.md
claude "Given this project context: [paste relevant sections from claude.md], help me with [specific task]"
```

---

# Flow

## Dev

### Setup
```bash
claude --dangerously-skip-permissions
````

- fill project information in CLAUDE.md
- Ask him to prepare a development plan
- Ask him to prepare basic folder structure
- Ask him to choose minimal dependencies
- Update CLAUDE.md

### Run your first Claude Code command

* **React**

  ```bash
  claude "Generate a project structure for my project using CLAUDE.md information with the following requirements:
  - Testing setup
  - Basic folder structure following best practices
  - Configuration files for testing
  - A simple README.md
  - Package/dependency management setup"
  ```

* **Python**

  ```bash
  claude "Generate a project structure for my 'Project Overview' using CLAUDE.md information with the following requirements:
  - Testing setup to check testing setup
  - add missing dependencies from 'Dependencies' section
  - Basic folder structure following best practices
  - Configuration files for testing
  - A simple README.md
  "
  ```

### Check installation

* **React**

  ```bash
  npm install
  npm run dev
  npm test
  ```

* **Python**

  ```bash
  poetry install
  poetry run python -m pytest
  ```

### Update `CLAUDE.md`

```bash
claude "Update @CLAUDE.md with current project folder structure"
```

```bash
claude "Update @CLAUDE.md with current project folder structure and new commands"
```

### Implementation flow

```bash
claude "Develop a part of this user story: [story] with corresponding unit tests: [part]"
```

```bash
claude "Develop a next part of current user story with corresponding minimal unit tests: [part]"
```

```bash
claude "Create a implementation plan for this 'Project Overview' locatecd in @CLAUDE.md.
- I want to have modular plan that will allow to work in small iterative steps.
- This is Proof of Concept application not production ready app.
- Include minimal necessary dependencies needed to develop the project
```

```bash
# Turn plan mode on

claude "Develop following part of the application from Phase [x]: [part].
Create minimal tests and at the end of your work summarize what you did and why this is important from project perspective.
```

```bash
claude "Refactor this code for better [performance/readability]: [code]"
```



### Workbook


```bash
claude "Check if you have the ability to run and test this application. Use @CLAUDE.md for project information."
```

```bash
claude "Create a implementation plan for this 'Project Overview' locatecd in @CLAUDE.md.
- I want to have modular plan that will allow to work in small iterative steps.
- This is Proof of Concept application not production ready app.
- Include minimal necessary dependencies needed to develop the project
```

```bash
claude "Update @CLAUDE.md with current project folder structure, new commands and dependencies"
```

```bash
claude "Develop following part of the application from Phase 3: Web Interface Foundation
- Set up ASP.NET Core web application
- Create basic controller and views
- Username prompt page/modal
- Chat message display area
Create minimal tests and at the end of your work summarize what you did and why."
```

```bash
claude "Check if your changes are aligned with overall Project goals and are moving the development in completion direction."
```
