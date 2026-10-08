# ADR 0001: Initial Platform Architecture

- **Status:** Accepted
- **Date:** 2026-10-06

## Context

File2FormAI must support citation-backed equipment troubleshooting for multiple organizations without leaking documents, sessions, retrieval results, tool activity, or cached data between them. The first use case is Army maintenance, but the product must remain usable for other maintenance and industrial domains.

The first MVP must let two organizations configure equipment, ingest manuals, and independently ask grounded questions. The team needs an architecture that is straightforward to build and test now, yet has explicit seams for AI providers, parsers, identity providers, durable workflows, and approved external tools later.

Important constraints include:

- a small initial product surface and no demonstrated need for distributed domain services;
- evidence provenance down to immutable document versions and page locators;
- tenant isolation across synchronous and asynchronous paths;
- provider and domain terminology that will evolve; and
- no verified dependency compatibility matrix yet.

## Decision

### 1. Use a monorepo and modular monolith

The React SPA will live in `apps/web`. FastAPI, background worker entry points, domain modules, persistence, and provider adapters will live in `backend`. API and worker processes may be deployed separately, but they share application services and a data model.

Domain modules own cohesive behavior and publish explicit service contracts. HTTP routes, worker entry points, and LangGraph nodes remain thin adapters. FastAPI is the only application API.

### 2. Make organization the primary tenant boundary

`Organization` owns settings, equipment, documents, sessions, evidence, agent configurations, and tools. `User` is global and gains organization-specific roles only through `Membership`.

Every tenant-owned service and repository operation requires `organization_id` from an authorized request or job context. Tenant-owned rows carry that ID, related records are validated as belonging to the same organization, and composite database constraints are used where practical. The same scope is mandatory for storage keys, retrieval predicates, jobs, streams, tool calls, Redis state, and frontend query keys.

OIDC/JWT is the production identity direction, with Keycloak as a replaceable local identity provider. A development identity adapter is allowed only behind an explicit development-only setting and must fail closed elsewhere. Production authentication is required before an external pilot.

### 3. Keep data and retrieval in PostgreSQL initially

PostgreSQL is the system of record. pgvector supports semantic search and PostgreSQL full-text search supports lexical search. The retrieval module executes both with the same tenant/equipment/document constraints and initially combines their ranks using reciprocal-rank fusion.

Redis is transient coordination and cache infrastructure, not the authoritative record. S3-compatible object storage holds source documents; MinIO is the planned local implementation.

### 4. Preserve evidence as first-class data

Documents have immutable source versions. Chunks retain page-aware locators. Each answer records the retrieved evidence actually provided to the model, including ranks and snapshots, and citations can refer only to that evidence. Insufficient or conflicting evidence produces a clarification or explicit limitation.

An LLM response is not proof of an external action. Tool actions may be claimed only from recorded successful results.

### 5. Put variable integrations behind application ports

The application defines `DocumentParser`, `EmbeddingProvider`, `LLMProvider`, `ToolRegistry`, and `ToolExecutor` interfaces. PyMuPDF, OpenAI embeddings, the OpenAI Responses API, and the official MCP Python SDK are initial adapters. Automated tests use deterministic fakes.

LangGraph coordinates one explicit troubleshooting workflow initially. Authorization, retrieval, persistence, and tool policy remain in application services rather than graph nodes. Durable checkpointing is deferred.

### 6. Separate tenant configuration from invariants

Branding, terminology, equipment, document applicability, approved agent settings, retrieval tuning within limits, and tool allowlists are organization configuration. Tenant isolation, authorization, evidence provenance, citation validation, auditability, and honest reporting of actions are fixed platform behavior.

Prompts are version-controlled artifacts. Published agent configurations reference exact prompt/workflow/provider configuration revisions.

### 7. Defer dependency and worker selection until implementation

The agreed technologies define direction, not version numbers. Compatible dependency versions will be verified and locked when the relevant application or integration is bootstrapped. The worker library remains undecided until ingestion semantics, retries, scheduling, and operational requirements are implemented.

## Consequences

### Positive

- One codebase and database keep early transactions, migrations, testing, and operations manageable.
- Module boundaries and provider ports allow implementations to change without moving business policy into vendor SDKs.
- PostgreSQL hybrid retrieval avoids a separate vector database while the corpus and scale are unknown.
- Explicit organization scope and same-tenant constraints make leakage harder and testable at multiple layers.
- First-class evidence and immutable versions support citation navigation, audits, and retrieval evaluation.
- Domain-neutral configuration permits new verticals without forking the platform core.

### Costs and risks

- A modular monolith requires discipline to prevent cross-module repository access and accidental coupling.
- Duplicating `organization_id` on tenant-owned rows adds schema and mapping work but enables enforceable boundaries.
- Hybrid retrieval quality depends on corpus-specific chunking, thresholds, and evaluation; RRF is a starting point, not a guarantee.
- PostgreSQL and object storage require coordinated lifecycle and backup policy so citations do not outlive their sources unexpectedly.
- Separate API and worker processes introduce enqueue-after-commit and idempotency concerns even within a monolith.
- Provider abstractions can become lowest-common-denominator interfaces if they are generalized before real use cases.

## Alternatives considered

### Microservices from the start

Rejected for the MVP. They would add distributed authorization, consistency, deployment, and observability complexity before independent scaling or team ownership requires it. Module boundaries preserve a later extraction path.

### Dedicated vector database

Deferred. PostgreSQL already owns authorization and document metadata, and pgvector keeps filtered search close to those constraints. A dedicated service can be reconsidered only with measured scale or retrieval requirements and an equally strong tenant-filter design.

### Provider SDKs directly in routes or workflow nodes

Rejected. This would couple business behavior and tests to vendors and make authorization, evidence handling, and error normalization inconsistent.

### Framework-owned agent architecture

Rejected. LangGraph is an orchestration adapter for one workflow, not the owner of domain policy or persistence. This limits lock-in and keeps non-AI service behavior testable.

### Shared users with a single organization field

Rejected. Users must be able to belong to multiple organizations with different roles; `Membership` models that relationship explicitly.

## Follow-up decisions

Future ADRs should resolve at least:

- worker library and reliable enqueue/outbox design;
- PostgreSQL row-level security;
- production identity provider and authorization model;
- durable LangGraph checkpointing and human approvals;
- streaming transport;
- document parsing beyond text PDFs and content security controls;
- embedding migration and vector indexing strategy;
- retention, deletion, legal hold, and audit policy;
- deployment, secrets, observability, data residency, and provider fallback; and
- MCP approval, sandboxing, credential, and result-redaction policy.
