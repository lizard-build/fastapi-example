# FastAPI deployment example

A small FastAPI app with a health endpoint and a JSON echo endpoint. The Procfile starts Uvicorn on `0.0.0.0:8000`. This example is prepared for Lizard (lizard.build).

## Run locally

Use Python 3.13:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/openapi.json
curl --fail -H 'Content-Type: application/json' \
  -d '{"message":"hello"}' http://localhost:8000/echo
```

Expect `{"status":"ok"}`, an OpenAPI document, and `{"echo":{"message":"hello"}}`. `/docs` provides the interactive API docs. A missing route should return 404.

## Deploy

```bash
npm install -g @lizard-build/cli
lizard login
lizard init --name fastapi-example
lizard add --service api
lizard up --service api --port 8000
```

Repeat the checks against the returned HTTPS URL. Keep the Procfile in the source upload and leave service start overrides unset. Exclude the virtual environment and secrets.

See the [FastAPI guide](https://lizard.build/docs/framework-guides/fastapi/) for custom import paths, logs, and database configuration. The health response only checks that this process serves requests; it does not check an external database or dependency.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests start the production Uvicorn entry point and check health, Swagger UI, OpenAPI, JSON echo, invalid input, and a missing route. GitHub Actions runs the same checks on Linux with Python 3.13. All dependencies are pinned in `requirements.txt`.

## Cloud check

On 9 September 2026, six public HTTPS checks passed on Lizard for commit `df522c15f2771704ec2ab28aadda47293d6ea3b1`. See the [dated results and configuration](deployment-checks/2026-09-09.json), [live health endpoint](https://crawl-timber-nt5k.eu-west-lim-a.onlizard.com/health), and [API interface](https://crawl-timber-nt5k.eu-west-lim-a.onlizard.com/docs).

This is a small app without a database. The checks cover HTTP behavior, not uptime or performance under load. Resource cost rates in the record are point-in-time readings, not a monthly bill. The [Python hosting guide](https://lizard.build/blog/python-app-hosting) explains the wider choice of app, worker and database configuration.

## License

MIT. See [LICENSE](LICENSE).
