"""Add a fingerprint to the site's own stylesheets (e.g. extra.css?v=1a2b3c4d)
so browsers fetch the new version as soon as it changes, rather than showing
a cached copy for a while after each deploy."""
import hashlib
from pathlib import Path


def on_config(config):
    docs = Path(config["docs_dir"])
    busted = []
    for css in config["extra_css"]:
        path = str(css).split("?")[0]
        file = docs / path
        if file.exists():
            digest = hashlib.md5(file.read_bytes()).hexdigest()[:8]
            busted.append(f"{path}?v={digest}")
        else:
            busted.append(css)
    config["extra_css"] = busted
    return config
