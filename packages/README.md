# Packages

The `packages/` directory stores the individual Python packages for this monorepo. This includes a ["core" package](./pkg-core/), with code that is meant to be shared across any other package/project in this monorepo, including a `setup_logging()` function to simplify initializing logging from new entrypoints.

Each package is its own isolated `pdm` project, with its own `pyproject.toml`, dependencies, etc. When creating a new project, make sure to add it to the [project's `pyproject.toml`](../pyproject.toml) so it will be built & installed when `pdm lock && pdm install` is run.

## Initializing a new package

*WIP*

## Adding package as a dependency in another package

*WIP*
