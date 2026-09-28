"""./buildSite: check, build, lock, verify and preview a DreamWeave mod site."""

import argparse
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

from . import build, gitrepo, migrate, offline, sitecheck
from .problems import InvalidRepository

COMMANDS = ("check", "build", "lock", "verify", "serve", "new-id", "zola-version")


def command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="buildSite",
        description="Validate, package and publish DreamWeave mod projects. Run from anywhere in the repository.",
        epilog="Don't forget to bring a towel.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("check", help="validate every project without writing anything")

    build_parser = commands.add_parser("build", help="package development builds and write the site's protocol files")
    build_parser.add_argument("--skip-archives", action="store_true", help="skip packaging (faster preview; development hashes are omitted)")

    lock_parser = commands.add_parser("lock", help="record a release's archive hash in mod.lock before tagging it")
    lock_parser.add_argument("slug", help="the project's slug from mod.toml")
    lock_parser.add_argument("--version", help="the release to lock (default: the newest unlocked [[releases]] entry)")

    verify_parser = commands.add_parser("verify", help="CI: rebuild a tagged release and fail unless it matches mod.lock")
    verify_parser.add_argument("tag", help="<slug>-<version>")

    links_parser = commands.add_parser("links", help="check the built site's local links, assets and anchors")
    links_parser.add_argument("--public", default="public", help="the built site (default: public)")
    links_parser.add_argument("--base-url", help="the URL it was built for (default: DREAMWEAVE_BASE_URL or config.toml)")

    commands.add_parser("schemas", help="validate the generated index and manifests against the published schemas")

    commands.add_parser("serve", help="write preview data, run `zola serve`, and regenerate when mod.toml or mod.lock change")
    migrate_parser = commands.add_parser("migrate", help="print a suggested mod.toml for a V3 page (writes nothing)")
    migrate_parser.add_argument("directory", help="the page's directory, e.g. content/my_mod")

    commands.add_parser("new-id", help="print a fresh project id (a random UUID)")
    commands.add_parser("zola-version", help="print the Zola version archives are rendered with")
    return parser


def repository_root() -> Path:
    return Path(gitrepo.run_git("rev-parse", "--show-toplevel").decode().strip())


def run_build(root: Path, skip_archives: bool) -> None:
    repository = build.load_repository(root)
    repository.problems.raise_if_any()
    build.clean_dist(root)
    build.write_changelog_stubs(repository)
    artifacts = build.build_development(repository, include_archives=not skip_archives)
    build.write_site(repository, artifacts, archives_built=not skip_archives)
    print(f"Wrote {build.INDEX_FILE} and {len(repository.projects)} project manifest(s) under {build.GENERATED_ROOT}/projects/")


def watched_state(root: Path) -> tuple:
    paths = sorted([*root.glob("content/**/mod.toml"), *root.glob("content/**/mod.lock"), *root.glob("content/**/index.md"), root / "config.toml"])
    return tuple((str(path), path.stat().st_mtime_ns) for path in paths if path.exists())


def run_serve(root: Path) -> None:
    run_build(root, skip_archives=True)
    process = subprocess.Popen(["zola", "serve"], cwd=root)
    state = watched_state(root)
    try:
        while process.poll() is None:
            time.sleep(1)
            current = watched_state(root)
            if current != state:
                state = current
                try:
                    run_build(root, skip_archives=True)
                except InvalidRepository as error:
                    print(error.render(), file=sys.stderr)
    except KeyboardInterrupt:
        process.terminate()
    process.wait()


def main(arguments: list[str]) -> int:
    options = command_parser().parse_args(arguments)
    if options.command == "new-id":
        print(uuid.uuid4())
        return 0
    if options.command == "zola-version":
        print(offline.ZOLA_VERSION)
        return 0
    if options.command == "migrate":
        suggestion, notes = migrate.suggest(Path(options.directory).resolve())
        print(suggestion, end="")
        for note in notes:
            print(f"note: {note}", file=sys.stderr)
        return 0

    root = repository_root()
    os.chdir(root)
    try:
        if options.command == "check":
            repository = build.load_repository(root)
            for note in repository.problems.notes:
                print(f"note: {note}")
            repository.problems.raise_if_any()
            print(f"OK: {len(repository.projects)} project(s).")
        elif options.command == "build":
            run_build(root, options.skip_archives)
        elif options.command == "lock":
            repository = build.load_repository(root)
            repository.problems.raise_if_any()
            build.lock_release(repository, options.slug, options.version)
            refreshed = build.load_repository(root, check_payloads=False)
            build.write_site(refreshed, {}, archives_built=False)
        elif options.command == "verify":
            repository = build.load_repository(root)
            repository.problems.raise_if_any()
            build.clean_dist(root)
            build.verify_tag(repository, options.tag)
        elif options.command == "links":
            import tomllib
            base_url = options.base_url or os.environ.get("DREAMWEAVE_BASE_URL") or tomllib.loads((root / "config.toml").read_text())["base_url"]
            checked, errors = sitecheck.check_site(root / options.public, base_url)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                print(f"{len(errors)} broken local link(s).", file=sys.stderr)
                return 1
            print(f"Checked {checked} local links, assets and anchors.")
        elif options.command == "schemas":
            checked, errors = sitecheck.check_protocol_documents(root)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print(f"{checked} protocol document(s) match their schemas.")
        elif options.command == "serve":
            run_serve(root)
    except InvalidRepository as error:
        print(error.render(), file=sys.stderr)
        return 1
    except (gitrepo.GitError, offline.OfflineError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0
