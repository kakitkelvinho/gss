# Simulator + MCP server. Sim source and hidden state live only in this container.
FROM python:3.12-slim

RUN pip install --no-cache-dir uv==0.9.7
WORKDIR /srv
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-default-groups --group server
COPY sim ./sim
COPY server ./server
RUN rm -rf sim/tests server/tests

EXPOSE 8000
CMD [".venv/bin/python", "-m", "server.app"]
