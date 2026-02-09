# scrolli_form — container instructions

Build the image with Podman:

```bash
podman build -t scrolli_form:latest .
```

Run the container (maps container port 7860 to host port 7860):

```bash
podman run -p 7860:7860 --rm scrolli_form:latest
```

Persist collected pledges to host by mounting the `output` directory:

```bash
mkdir -p output
podman run -p 7860:7860 -v "$(pwd)/output:/app/output" --rm scrolli_form:latest
```

To change the port the container listens on, set the `PORT` env var:

```bash
podman run -p 8000:8000 -e PORT=8000 --rm scrolli_form:latest
```
