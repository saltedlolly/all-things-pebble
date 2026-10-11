"""Add a fingerprint to the site's own stylesheets and scripts (e.g.
extra.css?v=1a2b3c4d) so browsers fetch the new version as soon as it
changes, rather than showing a cached copy for a while after each deploy."""
import hashlib
from pathlib import Path


def bust(docs, path):
    file = docs / path.split("?")[0]
    if not file.exists():
        return path
    digest = hashlib.md5(file.read_bytes()).hexdigest()[:8]
    return f"{path.split('?')[0]}?v={digest}"


def on_config(config):
    docs = Path(config["docs_dir"])
    config["extra_css"] = [bust(docs, str(css)) for css in config["extra_css"]]
    for script in config["extra_javascript"]:
        # Scripts are objects with a path, or plain strings in older MkDocs
        if hasattr(script, "path"):
            script.path = bust(docs, script.path)
    config["extra_javascript"] = [bust(docs, s) if isinstance(s, str) else s
                                  for s in config["extra_javascript"]]
    return config
