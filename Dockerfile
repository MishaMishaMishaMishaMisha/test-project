# install python
FROM python:3.14-slim

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# create user
RUN useradd -m -u 1000 appuser

# set env path for uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# create venv and give rights to user (/opt/venv)
RUN mkdir -p /opt/venv && chown -R appuser:appuser /opt/venv

WORKDIR /app

# give rights to user (/app)
RUN chown -R appuser:appuser /app

# switch to user
USER appuser

# add venv to path
ENV PATH="/opt/venv/bin:$PATH"

# copy requirements
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# install packages
RUN uv sync --frozen --no-install-project

# copy source code
COPY --chown=appuser:appuser src/ ./src/

# finish configuring venv and project
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

