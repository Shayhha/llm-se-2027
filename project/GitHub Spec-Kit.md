### GitHub/Spec-kit

https://github.com/github/spec-kit is a toolkit that extends code agents with PRD editing capabilities.  It is an alternative to OpenSpec.

`spec-kit` introduces spec-specific commands such as:

- `/speckit.constitution` Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
- `/speckit.specify` Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page. Albums are never in other nested albums. Within each album, photos are previewed in a tile-like interface.
- `/speckit.plan` The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.

Additional commands are available to manipulate specifications and break them down into tasks and implementation artifacts.

| Command              | Description                                                                                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `/speckit.tasks`     | Creates an actionable task list from your implementation plan.                                                                       |
| `/speckit.clarify`   | Clarify underspecified areas (recommended before `/speckit.plan`)                                                                    |
| `/speckit.analyze`   | Cross-artifact consistency & coverage analysis (run after `/speckit.tasks`, before `/speckit.implement`)                             |
| `/speckit.checklist` | Generate custom quality checklists that validate requirements completeness, clarity, and consistency (like "unit tests for English") |
| `/speckit.implement` | to execute all tasks and build your feature according to the plan.                                                                   |

