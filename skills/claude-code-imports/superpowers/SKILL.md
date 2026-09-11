---
name: superpowers
description: Serious development and strict workflows. Forces clarify → spec → plan → execute → review sequence with strict TDD ensuring a failing test is written before any implementation code.
---

# Superpowers

Welcome, Developer

## The Rule

**Before any code is written, you MUST follow the clarify → spec → plan → execute → review sequence.**

### 1. Clarify
- Understand the request fully
- Ask clarifying questions before proceeding

### 

### 

### 2. Spec
- Write a design document before implementation
- Capture requirements, interfaces, and edge cases
- Get user approval on the spec

### 3. Plan
- Create an implementation plan using the writing-plans skill
- Break down tasks and estimate effort

### 4. Execute (TDD)
- **Write a failing test first** (Red step)
- Only then write implementation code
- Run tests to verify they fail initially

### 5. Review
- Review all changes
- Ensure tests pass
- Verify the implementation meets the spec

## Red Flags (rationalization stoppers)

| Thought | Reality |
|---------|---------|
| "This is just a simple fix" | All tasks follow the sequence |
| "I already know what to build" | Spec must be written and approved |
| "Let me just check the code quickly" | Full clarify cycle required |
| "Tests can wait" | TDD: test must fail before code |
| "This will be quick, no need for planning" | Planning is mandatory |

## Checklist

- [ ] Clarify: All questions answered, request understood
- [ ] Spec: Design document written and user-approved
- [ ] Plan: Implementation plan created via writing-plans
- [ ] Execute: Failing test written before any code
- [ ] Review: Changes reviewed, tests passing

## Process Flow

```
Classify & Clarify → Write Spec → Get Approval → 
Write Failing Test → Implement Code → Run Tests → 
Review & Refactor → User Approval
```