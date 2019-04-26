FROM python:3-slim AS builder

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)
RUN apt-get update && apt-get install -y --no-install-recommends curl ${ADDITIONAL_PACKAGE} \
    && echo "Pulling watchdog binary from Github." \
    && curl -sSLf https://github.com/openfaas-incubator/of-watchdog/releases/download/0.5.1/of-watchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog \
    && apt-get remove -y curl \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /wheels
COPY requirements.txt .
USER root
RUN pip wheel -r requirements.txt
COPY function/requirements.txt	./function_requirements.txt
RUN pip wheel -r function_requirements.txt

# Multi-stage build
FROM python:3-slim

# Add non root user
RUN addgroup --system app && adduser --system --ingroup app app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

COPY --from=builder /usr/bin/fwatchdog /usr/bin/fwatchdog
COPY index.py           .
COPY requirements.txt   .
COPY --from=builder /wheels /wheels

USER root
RUN pip install -r requirements.txt -f /wheels

USER app
RUN mkdir -p function
RUN touch ./function/__init__.py
WORKDIR /home/app/function/
COPY function/requirements.txt	.
RUN pip install --user -r requirements.txt -f /wheels

WORKDIR /home/app/

USER root
COPY function   function
RUN chown -R app:app ./function

USER app
# Set up of-watchdog for HTTP mode
ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
