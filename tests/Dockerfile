# Separate verifier image (Harbor does not upload tests/ in separate mode; it is baked in here).
# It only reads the artifacts collected from the sim container (/gss/out) and writes the reward.
FROM python:3.12-slim
COPY . /tests/
RUN chmod +x /tests/test.sh
