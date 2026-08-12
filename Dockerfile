FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . "towerctl-core[redis] @ git+https://github.com/towerctl/core@main"
EXPOSE 8082
CMD ["uvicorn", "evals.main:app", "--host", "0.0.0.0", "--port", "8082"]
