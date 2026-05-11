# Portable Binwalk Server

Run from this directory:

```bash
python binwalkServer.py --workers=15
```

Default director URL: `http://127.0.0.1:8080`

Choose a different director port:

```bash
python binwalkServer.py --workers=15 --port=9090
```

Detect a file:

```bash
curl -X POST http://127.0.0.1:8080/detect \
  -H 'Content-Type: application/json' \
  -d '{"filePath":"/path/to/file"}'
```

This bundle contains the local Binwalk Python package, magic files, plugins,
and the fast director/worker server. It does not require installing Binwalk as
a site package. Use a reasonably current Python 3 runtime.
