# EyeD Project Rules

## Overview
This directory contains foundational rules and guidelines for rebuilding the EyeD project with clean architecture, SOLID principles, and maintainable code.

## Rule Files

### 1. [architecture.md](./architecture.md)
**Purpose**: Defines high-level architecture, layer separation, and SOLID principles.

**Key Topics**:
- Clean Architecture layers (Presentation → Application → Domain → Infrastructure)
- Dependency rule (dependencies point inward only)
- Single Responsibility Principle (SRP)
- Service size limits (max 300 lines per class)
- Anti-patterns from old code (God classes, mixed concerns)

**When to Reference**:
- Designing new features
- Refactoring existing code
- Creating new services or modules
- Ensuring layer boundaries are respected

### 2. [naming.md](./naming.md)
**Purpose**: Defines consistent naming conventions for all components.

**Key Topics**:
- Python naming conventions (PascalCase, snake_case, UPPER_SNAKE_CASE)
- Layer-specific naming (entities, services, use cases, repositories)
- Method naming (action verbs, boolean prefixes)
- File and folder naming
- Anti-patterns (abbreviations, generic names, Hungarian notation)

**When to Reference**:
- Creating new classes, methods, or files
- Naming variables and constants
- Organizing project structure

### 3. [coding_guidelines.md](./coding_guidelines.md)
**Purpose**: Defines coding standards, style, and best practices.

**Key Topics**:
- PEP 8 compliance (line length, indentation, imports)
- Type hints (always required)
- Docstrings (Google style)
- Error handling (specific exceptions)
- Logging (structured logging)
- Testing (organization and naming)
- Code review checklist

**When to Reference**:
- Writing new code
- Reviewing code
- Setting up tests
- Handling errors

### 4. [microservices.md](./microservices.md)
**Purpose**: Defines rules for creating self-contained, modular components.

**Key Topics**:
- Self-contained modules (independent, reusable, testable)
- Module communication (interfaces, DTOs, dependency injection)
- Service boundaries (one service = one domain concern)
- Folder structure by feature
- Anti-patterns (tight coupling, shared state, God services)

**When to Reference**:
- Creating new modules or services
- Designing module interfaces
- Organizing code by feature
- Ensuring modules are independent

### 5. [migration_guide.md](./migration_guide.md)
**Purpose**: Step-by-step guide for migrating from Streamlit to Next.js.

**Key Topics**:
- Architecture changes
- Phase-by-phase migration steps
- Code examples for API and frontend
- Testing migration
- Rollback plan

**When to Reference**:
- Planning migration from Streamlit
- Implementing REST API layer
- Building Next.js frontend
- Troubleshooting migration issues

### 6. [ux_ui_principles.md](./ux_ui_principles.md)
**Purpose**: Defines clean UI/UX patterns for Next.js frontend.

**Key Topics**:
- Separation of concerns (UI only handles presentation)
- Component structure (stateless, reusable React components)
- Next.js App Router patterns
- WebRTC + Canvas camera capture
- REST API client patterns
- State management (Zustand for UI state only)
- Anti-patterns (business logic in UI, direct service access)

**When to Reference**:
- Creating React components
- Building Next.js pages
- Handling user interactions
- Designing forms and visualizations
- Implementing camera capture
- API integration

## How to Use These Rules

### For Future Development

1. **Before starting work**: Review relevant rule files
2. **During development**: Reference rules when making decisions
3. **Before committing**: Check against code review checklist
4. **When refactoring**: Ensure code follows all rules

### For AI Agents

When generating or refactoring code:

1. **Read architecture.md first**: Understand layer structure
2. **Check naming.md**: Use correct naming conventions
3. **Follow coding_guidelines.md**: Write clean, documented code
4. **Apply microservices.md**: Create focused, independent modules
5. **Reference ux_ui_principles.md**: Build clean UI components

### Quick Reference Checklist

Before submitting code, verify:

- [ ] Follows Clean Architecture layers
- [ ] Single Responsibility Principle (one class = one purpose)
- [ ] Dependencies point inward only
- [ ] Uses correct naming conventions
- [ ] Includes type hints and docstrings
- [ ] Handles errors with specific exceptions
- [ ] Uses dependency injection (no direct instantiation)
- [ ] Classes < 300 lines, methods < 50 lines
- [ ] No business logic in UI components (CRITICAL: Frontend is presentation only)
- [ ] Frontend calls REST API only (no direct use case or service access)
- [ ] API layer is thin adapter (calls use cases, no business logic)
- [ ] Tests are written and passing

## Key Principles Summary

### SOLID Principles
- **S**ingle Responsibility: One class = one purpose
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes must be substitutable
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

### Clean Architecture
- **Presentation**: Next.js frontend + REST API (user interaction only, NO business logic)
- **Application**: Use cases (orchestration)
- **Domain**: Business logic (pure, no infrastructure)
- **Infrastructure**: Data access, external services

### Modularity
- Self-contained modules
- Clear boundaries (interfaces)
- Independent and testable
- Grouped by feature/domain

## Anti-Patterns to Avoid

Based on analysis of the old codebase:

1. **God Classes**: Services with 600+ lines doing everything
2. **Mixed Concerns**: Business logic in repositories, data access in services
3. **Tight Coupling**: Direct instantiation instead of dependency injection
4. **Backward Compatibility Bloat**: Multiple methods doing the same thing
5. **Business Logic in UI**: Components fetching data and applying business rules (CRITICAL: Frontend must NOT contain business logic)
6. **Magic Numbers**: Hard-coded values instead of named constants
7. **Deep Nesting**: 5+ levels of indentation
8. **Generic Names**: `process()`, `handle()`, `data` instead of descriptive names
9. **Frontend Business Logic**: Calculating badges, validating attendance rules, or any business rules in React components
10. **Direct Service Access**: Frontend accessing use cases or domain services directly (must go through REST API)

## Migration Strategy

When rebuilding:

1. **Start with domain layer**: Pure business logic, no dependencies
2. **Build infrastructure**: Repositories, storage, external services
3. **Create use cases**: Orchestrate domain services
4. **Build REST API**: Thin adapter layer that calls use cases
5. **Build Next.js frontend**: Presentation layer that calls REST API (NO business logic)
6. **Add tests**: Unit → Integration → E2E

**Migration from Streamlit**:
- See [migration_guide.md](./migration_guide.md) for detailed step-by-step instructions
- Create FastAPI REST API layer
- Build Next.js frontend with WebRTC + Canvas for camera
- Migrate state management from Streamlit session state to Zustand
- Replace Streamlit forms with React Hook Form + Zod validation

## Questions?

If you're unsure about how to apply these rules:

1. Check the relevant rule file
2. Look for examples (✅ CORRECT) and anti-patterns (❌ WRONG)
3. Review the "Future Agent Instructions" sections
4. When in doubt, favor smaller, more focused components

---

**Remember**: These rules are designed to prevent the bloat and complexity that accumulated in the old codebase. Follow them strictly to maintain a clean, maintainable codebase.







