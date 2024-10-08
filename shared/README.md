# Shared

Domain-level code that is shared by any app/package/project in this repository. Shared code lives outside the [`packages/`](../packages/) namespace to avoid `ModuleImportError`s.

Code in this namespace should be decoupled from app/package functionality. These modules can be services like a database interface, or to store classes like in [`shared/domain/`](./domain/). A global HTTP client (with optional caching) can be imported from [`shared/http-lib`](./http-lib/).
