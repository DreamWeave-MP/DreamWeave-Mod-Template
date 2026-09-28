"""Print a suggested mod.toml for a V3 page. Reads, never writes: the author reviews and saves it.

The slug keeps V3's title slug so existing <slug>-<version> tags stay this project's history.
Every data directory V3 listed stays installed, so the archive and install behave as before;
splitting them into optional components is a decision for the author, not for a converter.
"""

import datetime
import json
import re
import subprocess
import uuid
from pathlib import Path

from .model import read_frontmatter
from .versions import DECIMAL, NUMERIC, Version, VersionError

V3_EXTRA_KEYS = (
    "version", "install_info", "nexus_id", "nexus_group_id", "offsite_host", "is_binary", "game",
    "hide_download_bar", "stable_title", "dev_title", "show_only_description", "use_toc", "content_files",
)


def legacy_slug(title: str) -> str:
    text = re.sub(r"[\s\-]+", "_", title.lower().strip())
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_list(values: list[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def meaningful(values) -> list:
    return [value for value in (values or []) if not str(value).startswith("#")]


def tags_for(directory: Path, slug: str) -> list[tuple[str, str]]:
    """(version text, date) for every <slug>-<version> tag."""
    output = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short) %(creatordate:short)", f"refs/tags/{slug}-*"],
        cwd=directory, capture_output=True, text=True,
    ).stdout
    return [(tag[len(slug) + 1:], date) for tag, date in (line.split(" ", 1) for line in output.splitlines())]


def ordering_violations(history: list[tuple[str, str]], scheme: str) -> list[str]:
    parsed = []
    for text, date in history:
        try:
            parsed.append((Version.parse(text, scheme), date))
        except VersionError:
            return [f"{text} is not a {scheme} version"]
    ordered = sorted(parsed, key=lambda item: (item[1], item[0].precedence_key()))
    return [
        f"{later} ({later_date}) sorts below {earlier} ({earlier_date})"
        for (earlier, earlier_date), (later, later_date) in zip(ordered, ordered[1:])
        if later < earlier
    ]


def suggest(directory: Path) -> tuple[str, list[str]]:
    frontmatter = read_frontmatter(directory / "index.md")
    if frontmatter is None:
        raise SystemExit(f"{directory}/index.md has no frontmatter.")
    extra = frontmatter.get("extra") or {}
    title = frontmatter.get("title")
    if not title:
        raise SystemExit(f"{directory}/index.md has no title.")

    candidates = [legacy_slug(title), legacy_slug(directory.name)]
    slug = next((candidate for candidate in candidates if tags_for(directory, candidate)), candidates[0])
    notes = []
    lines = [
        f"# Migrated from V3 frontmatter in {directory.name}/index.md. Review every line, then save as mod.toml.",
        f"id = {toml_string(str(uuid.uuid4()))}",
        f"slug = {toml_string(slug)}  # matches the existing {slug}-<version> tags, so they stay this project's history",
    ]
    if extra.get("is_binary"):
        lines.append('type = "tool"')
    if extra.get("game") and extra["game"] != "morrowind":
        lines.append(f"game = {toml_string(extra['game'])}")

    offsite = extra.get("offsite_host")
    if offsite:
        lines += ["", "[links]"]
        if offsite.get("provider", "github") == "github":
            lines.append(f'source = "https://github.com/{offsite["owner"]}/{offsite["repo"]}"')
        notes.append(
            "offsite_host: V4 packages what is in this repository. A mod released from another repository "
            "should publish its own mod.toml and manifest there; this page can link to it instead."
        )

    install = extra.get("install_info") or {}
    data_directories = meaningful(install.get("data_directories"))
    content_files = meaningful(install.get("content_files")) or meaningful(extra.get("content_files"))
    fallback_entries = {key: value for key, value in (install.get("fallback_entries") or install.get("fallback") or {}).items() if not str(key).startswith("#")}
    config = meaningful(install.get("config"))

    lines += ["", "[runtimes]", 'openmw = "*"  # narrow this to the versions you have tested, e.g. ">=0.49"', "", "[openmw]"]
    if data_directories and data_directories != ["."]:
        lines.append(f"data_directories = {toml_list(data_directories)}")
    if content_files:
        lines.append(f"content_files = {toml_list(content_files)}")
    if config:
        if config != ["."]:
            notes.append(f"install_info.config listed {config}; V4 supports an openmw.cfg in the project root (config = true). Move the others or drop them.")
        lines.append("config = true")
    if fallback_entries:
        lines.append("")
        lines.append("[openmw.fallback_entries]")
        for key, value in fallback_entries.items():
            lines.append(f"{toml_string(key)} = {toml_string(str(value))}")
    if len(data_directories) > 1:
        notes.append(
            f"{len(data_directories)} data directories are all installed together, as in V3. To let players choose, "
            'switch to [package] format = "bain" or "fomod" and declare [[components]]; see the guide.'
        )

    if "nexus_id" in extra or "nexus_group_id" in extra:
        lines += ["", "[nexusmods]"]
        if "nexus_id" in extra:
            lines.append(f"mod_id = {int(extra['nexus_id'])}")
        if "nexus_group_id" in extra:
            lines.append(f"file_group_id = {toml_string(str(extra['nexus_group_id']))}")

    history = tags_for(directory, slug)
    current_text = str(extra.get("version", "")).strip()
    if current_text and all(text != current_text for text, _ in history):
        page_date = frontmatter.get("date")
        date = page_date.isoformat() if isinstance(page_date, datetime.date) else datetime.date.today().isoformat()
        history.append((current_text, date))

    numeric_problems = ordering_violations(history, NUMERIC)
    decimal_problems = ordering_violations(history, DECIMAL)
    scheme = NUMERIC
    if numeric_problems and not decimal_problems:
        scheme = DECIMAL
        lines.insert(3, 'versioning = "decimal"  # these releases were numbered like decimals: 0.82 comes before 0.9')
    elif numeric_problems:
        notes.extend(f"release history does not sort under either scheme: {problem}. Fix or drop those entries." for problem in numeric_problems)

    for text, date in sorted(history, key=lambda item: item[1]):
        lines += ["", "[[releases]]", f"version = {toml_string(text)}", f"date = {date}"]
    if history:
        notes.append(
            "Tagged releases published before V4 have no recorded hash, so the manifest leaves them out and the "
            "changelog marks them unverified. Lock and tag your next release to publish it to the network."
        )

    stale = [key for key in V3_EXTRA_KEYS if key in extra]
    if stale:
        notes.append(f"Then delete these from index.md's [extra]: {', '.join(stale)}.")
    return "\n".join(lines) + "\n", notes
