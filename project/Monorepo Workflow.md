## Monorepo 

When dealing with large-scale projects, organized in independent modules (front-end with many components, multiple micro-services), two approaches can be used to organize the Github repository of the project:
- Mono-repo: a single repository is used for the whole project with all its sub-components.
- Multi-repo: multiple Git repositories are created for each deployable unit (for example, one repo per micro-service).

For the project, we will use a mono-repo approach.  This has some benefits and some costs.  This page describes the trade-off and the workflow to be applied to minimize the costs of using a mono-repo approach.

Typical architectures combine a Next/React frontend with Python micro-service backend deployed into a cloud or Docker-based ecosystem.

A **Monorepo** (Monolithic Repository) with this technology stack allows us to treat  infrastructure, frontend, and microservices as a single cohesive unit, rather than isolated silos.


### Part 1: Monorepo vs. Multi-repo

To understand the best approach, we must visualize how the code is stored and accessed.

#### The Multi-repo Approach

In a traditional **Multi-repo** setup, the Next.js app lives in one Git repository, and each Python micro-service in another, and perhaps the shared configurations and persistence models in a third.

- **Friction:** If the Python team changes an API endpoint, they merge their PR. The Frontend team might not know this happened until their app breaks in the staging environment.
    
- **Version Drift:** The Frontend might be expecting `v1.2` of the API, but the backend is running `v1.3`.
    
- **Context Switching:** Developers and coding agents have to clone, install, and update multiple repositories to run the full stack locally.

#### The Monorepo Approach

In a **Monorepo**, the Next.js frontend and Python backend live side-by-side in distinct folders within the _same_ Git repository.

**Key Benefits for our Stack**

1. **Atomic Changes:** You can submit a single Pull Request (PR) that updates the Python API endpoint _and_ the React component that consumes it simultaneously. The app does not break because the changes land together.
    
2. **Shared Truth:** We keep our API definitions (e.g., OpenAPI specs or Database schemas) in a shared folder. If the backend changes the schema, the frontend build can be configured to fail immediately, catching errors before deployment.
    
4. **Simplified CI/CD:** We have one pipeline. We don't need to coordinate complex webhooks between repositories to run integration tests.

| **Feature**         | **Multi-repo**                     | **Monorepo**                           |
| ------------------- | ---------------------------------- | -------------------------------------- |
| **Code Visibility** | Siloed (Team A sees Repo A)        | Transparent (Everyone sees everything) |
| **Dependency Mgmt** | Hard (requires package publishing) | Easy (direct file imports/workspaces)  |
| **Refactoring**     | Slow (requires coordination)       | Fast (atomic commits)                  |
| **Dev Environment** | Complex (multiple terminals/repos) | Unified (one command startup)          |

### Part 2: Organizational Structure

For a mixed-language monorepo (TypeScript/JavaScript + Python), structure is critical. We want to separate concerns while allowing integration.

**Recommended Directory Tree:**

```
Project-monorepo/
├── README.md
├── package.json               # Root scripts
├── pnpm-workspace.yaml        # JS Workspace config
├── .github/
│   ├── workflows/             # CI/CD workflows
│   └── CODEOWNERS
├── build/                     # Monorepo build configuration
│   ├── compose.yaml           # Docker compose configuration for integration
│   └── mise.toml / justfile   # one entry point for every task
│
├── openspec/                  # Specifications
├── docs/
│   ├── adr/                   # Decision records
│   ├── journal.md             # Journal of the team
│   ├── glossary.md            # Ubiquitous language of the domain
│   └── verifiability.md       # Indicate how each spec item can be verified
│
├── apps/
│   ├── web/                   # Next.js Application
│   │   ├── package.json
│   │   └── src/...
│   └── data-exploration/      # UI Application to explore dataset
│       ├── package.json
│       └── src/...
│
├── services/
│   ├── api1/                  # Python Microservice (Cloud Run or Docker)
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   └── api2/                  # Python Microservice (Cloud Run or Docker)
│       ├── Dockerfile
│       ├── main.py
│       └── requirements.txt
│
└── packages/                  # Shared JS/TS Libraries
    ├── ui/                    # Shared React UI components
    ├── ts-types/              # Shared Types (generated from API specs)
    └── configs/               # Shared ESLint/TSConfig
```

- **`apps/`**: Contains deployable frontend units.
    
- **`services/`**: Contains deployable backend containerized services.
    
- **`packages/`**: Contains internal logic shared between frontend apps (or config files). _Note: You cannot directly import Python code into JS, but you can share config or generated types here._


### Part 3: Practical Workflow & Synchronization

Managing multiple teams (Frontend Team vs. Backend Team) in one repo requires specific tooling and rules.

#### 1. Tooling: The "Build System"

Since we have a mixed language stack, we need a tool that understands the dependency graph. **Nx** is often used for this, but it is complex for the scope of our projects.
Instead, we will use the following platform:

- **Python Modules**
  - **uv workspaces** to manage multiple Python projects from a unified uv environment.
  <https://www.danilchenko.dev/posts/uv-workspaces-monorepo/> provides instructions on how to setup the Python uv workspace.
  - Use the repo structure described above.
  ```
  repo/
  ├── openspec/                 # specs + change proposals (source of truth)
  ├── apps/web/                 # Next.js
  ├── services/<svc>/           # Python microservices (FastAPI)
  ├── packages/py-common/       # shared Python libs (models, auth, logging)
  ├── packages/ts-api-client/   # generated from OpenAPI — never hand-edited
  ├── docs/                     # MD docs, ADRs
  ├── compose.yaml
  └── mise.toml / justfile      # one entry point for every task
  ```
  - **FastAPI** with **Pydantic v2**, so types become API contracts.
- **TypeScript Modules (UI)**
  - pnpm workspaces with tsc --noEmit in strict mode as a CI gate, separate from next build.
  - ESLint with typescript-eslint.
  - Zod at runtime boundaries such as forms and environment variables.
- **Cross-language type contract**
  - Each FastAPI service exports `openapi.json`. Then `openapi-typescript` generates `packages/ts-api-client`. 
  - In CI, regenerate the client and fail the build on git diff. That way a Pydantic change that breaks the frontend fails at type-check time, not in production. This also fits OpenSpec well: a spec change leads to a model change, which leads to a regenerated client and a compiler-checked frontend.
- **Docker deployment**
  - Python: build from the repo root so the image can see shared packages. Use multi-stage builds and the uv dependency-layer method (`uv sync --frozen --no-install-workspace`) with `--mount=type=cache`
  - Next.js: output: "standalone" keeps the runtime image small.
  - Dev: `docker compose watch` gives hot reload. One compose.yaml covers all services.
- **Quality gates and docs**
  - pre-commit hook: type checks on staged files.
  - CI order: lint → type-check (pyright + tsc) → contract-drift check → tests (pytest / vitest) → image builds.
- **Docs** 
  - Markdown docs/ folder with ADRs. 
  - Use FastAPI’s auto-generated OpenAPI pages for API reference, and keep OpenSpec specs as the behavioral source of truth.
- **mise** for task running
  `mise` does three things:
  - **Tool versions** mise pins node, pnpm, uv and others in `mise.toml`, and a single mise install gives developers and CI runner the same versions. This replaces nvm and pyenv.
  - **Environment**: mise sets environment variables and loads .env files per directory.
  - **Tasks**: Tasks can depend on each other, run in parallel, and skip themselves when their sources/outputs haven’t changed. 
    - **Monorepo tasks**: Tasks under `services/*` and `apps/*` are discovered automatically, so mise //...:typecheck runs type checks everywhere. 


#### 3. Defining Ownership (`CODEOWNERS`)

In a large project, we could use the CODEOWNERS configuration in GitHub to automatically map PR review requests to specific teams based on the folder layout of the monorepo.  This would prevent "too many cooks in the kitchen." This enforces that specific teams must review changes in specific directories before a merge.


```
# .github/CODEOWNERS

# Frontend team owns the web app and UI packages
/apps/web/ @my-org/frontend-team
/packages/ui/ @my-org/frontend-team

# Backend team owns the Python services and Database schemas
/services/ @my-org/backend-team
/data.yaml @my-org/backend-team

# Both teams must agree on shared types or contracts
/packages/ts-types/ @my-org/frontend-team @my-org/backend-team
```

We can use this in our project or instead rely on discipline.

### Part 4: CI/CD Workflow (GitHub Actions)

In a multi-team monorepo, your CI pipeline acts as the traffic controller.

1. **Pull Request Opened:**
    - Pipeline checks which files changed.
    - If `services/api` changed -> Run Python Linting & Unit Tests.
    - If `apps/web` changed -> Run React Tests & Linting.
    - **Crucially:** Run an _Integration Test_ suite where the Next.js app hits the Python service inside the CI runner.
        
2. **Merge to Main:**
    - The pipeline detects changes.
    - **Frontend:** Builds Next.js and deploys the app.
    - **Backend:** Builds the Python Docker container and deploys to Google Cloud Run or locally on CI machine.



