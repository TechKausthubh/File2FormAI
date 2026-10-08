# File2FormAI Contributor Guide

## Scope

- File2FormAI is a generic, configurable, multi-tenant troubleshooting platform; never bake Army terminology or policy into the core.
- The repository contains the initial web/API development shell. Do not infer authorization, domain, ingestion, retrieval, agent, MCP, or voice behavior from the shell.
- Treat `docs/architecture.md`, `docs/data-model.md`, and accepted ADRs as the design baseline. Record material changes in an ADR.

## Target architecture

- Use a monorepo and modular monolith: `apps/web` owns the React SPA; `backend` owns FastAPI and worker modules.
- FastAPI is the only application API. Keep HTTP handlers thin and business rules in services.
- Keep domain modules cohesive. Cross module boundaries through explicit service contracts, not another module's repository or ORM internals.
- PostgreSQL is the system of record. Redis is transient coordination/cache infrastructure; object bytes live in S3-compatible storage.
- Put provider behavior behind `DocumentParser`, `EmbeddingProvider`, `LLMProvider`, `ToolRegistry`, and `ToolExecutor` interfaces.

## Non-negotiable invariants

- `Organization` is the tenant boundary. Every tenant-owned repository and service operation requires an explicit `organization_id` from an authorized request or job context.
- Never trust a tenant ID from an unvalidated body. Verify membership and same-organization relationships before reading or mutating data.
- Scope retrieval, object keys, jobs, sessions, tools, streams, logs, and frontend query keys by organization.
- Development identity must require an explicit development-only flag and fail closed in every other environment.
- Preserve immutable document versions, page locators, retrieved evidence, and citations.
- If evidence is insufficient, ask for clarification or state the limitation. Never imply a diagnostic or tool action happened without a recorded successful result.
- Tool access must be allowlisted, organization-scoped, validated, and audited.

## Change discipline

- Do not invent dependency versions. Choose and lock compatible versions only while implementing the relevant bootstrap or integration.
- Leave the background worker library undecided until ingestion is implemented.
- Every database change requires an Alembic migration; every functional change requires proportionate tests.
- Include cross-tenant negative tests for tenant-sensitive behavior and fake AI providers in automated tests.
- Keep prompts version controlled. Keep secrets, uploaded manuals, local databases, and generated sensitive data out of Git.
