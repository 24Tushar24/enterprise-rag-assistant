# Architecture

## Overview

The project is organized into a frontend, a Python backend, source data, and evaluation assets.

```text
User -> frontend -> backend API -> RAG pipeline
                                  |-> retrieval over data
                                  |-> generation model
                                  |-> evaluation helpers
```

## Backend boundaries

- `api` exposes HTTP endpoints.
- `services` coordinates application use cases.
- `rag` owns ingestion, retrieval, context assembly, and answer generation.
- `models` defines typed contracts.
- `core` contains configuration and infrastructure concerns.
- `evals` contains backend-side evaluation code.
