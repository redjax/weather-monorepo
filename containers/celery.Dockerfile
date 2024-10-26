# ARG PYTHON_BASE_IMG=3.11-slim
# FROM python:${PYTHON_BASE_IMG} AS base

# RUN pip install -U --no-cache pdm

# # Set the working directory in the container
# WORKDIR /project

# # Copy the main dependency files from the root project directory to the container
# COPY ./pyproject.toml ./pdm.lock ./

# FROM base AS stage

# COPY --from=base /project /project
# WORKDIR /project

# COPY apps/ /project/apps
# COPY packages/ /project/packages
# COPY scripts/ /project/scripts
# COPY shared/ /project/shared

# FROM base AS build

# COPY --from=stage /project /project

# WORKDIR /project

# # Install project dependencies
# RUN pdm install

# FROM build AS celery_worker

# COPY --from=build /project /project
# # WORKDIR /project

# ## Use virtualenv built at /project/.venv
# ENV PATH="/project/.venv/bin:$PATH"

# # ENTRYPOINT ["pdm", "run", "python", "/project/scripts/start_celery_worker.py"]
# ENTRYPOINT ["python", "/project/scripts/start_celery_worker.py"]

# # Optional debugging
# # RUN ls -la /project/scripts && sleep 10

# Specify the base Python image
ARG PYTHON_BASE_IMG=3.11-slim
FROM python:${PYTHON_BASE_IMG} AS base

# Install PDM to manage dependencies
RUN pip install -U --no-cache-dir pdm

# Set working directory
WORKDIR /project

# Copy dependency files early to leverage caching
COPY pyproject.toml pdm.lock ./

# Install dependencies in base stage to cache them
RUN pdm install --prod --no-editable

# ----------------------------------------------------------
# Build Layer: Installs all dependencies and prepares the project
# ----------------------------------------------------------
FROM base AS build

# Copy project files
COPY apps/ packages/ scripts/ shared/ /project/

# Install all dependencies (e.g., dev dependencies if needed)
RUN pdm install

# ----------------------------------------------------------
# Runtime Layer: Celery Worker
# ----------------------------------------------------------
FROM python:${PYTHON_BASE_IMG} AS celery_worker

# Set up the virtual environment path
ENV PATH="/project/.venv/bin:$PATH"

# Copy over installed dependencies and project files from the build layer
COPY --from=build /project /project

# Set working directory
WORKDIR /project

# Specify entrypoint for the celery worker
ENTRYPOINT ["python", "/project/scripts/start_celery_worker.py"]

# ----------------------------------------------------------
# Additional Runtime Layers for other services (optional)
# ----------------------------------------------------------

# Example for another runtime service
# FROM python:${PYTHON_BASE_IMG} AS another_service
# ENV PATH="/project/.venv/bin:$PATH"
# COPY --from=build /project /project
# WORKDIR /project
# ENTRYPOINT ["python", "/project/scripts/another_service.py"]
