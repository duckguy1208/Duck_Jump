# Contributing to Tie and Jon Pygame

Welcome! We use Gemini to help automate our development workflow.

## Using the Gemini Task Script

We have a helper script that allows you to trigger Gemini using the instructions defined in `prompt.md`. This is useful for autonomously picking up tasks from the `TODO.md`.

### Prerequisites

1.  **Gemini CLI**: Ensure you have the Gemini CLI installed and configured.
2.  **GitHub CLI**: The workflow uses `gh` for opening pull requests.

### Running the Task

To run the automated workflow, execute the following command in your terminal:

```powershell
.\auto-work.ps1
```

This script will:

1.  Read the current context and instructions from `prompt.md`.
2.  Invoke Gemini with the `-y` flag (auto-approving the initial prompt).
3.  Gemini will then follow the "Objective" in the prompt, which typically involves picking a task from `TODO.md`, creating a branch, and opening a PR.

## Manual Workflow

If you prefer to work manually, please:

1.  Create a branch for your feature or bugfix.
2.  Keep commits small and descriptive.
3.  Write tests for new behavior.
4.  Open a PR to `main` with a clear description of your changes.
