"""Repository-level operations: load and cross-check projects, build archives, write site data."""

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from . import fomod, gitrepo, offline, records
from .archive import ArchiveEntry, ArchiveResult, write_archive
from .model import (
    DEVELOPMENT_CHANNEL,
    EXAMPLE_PROJECT_IDS,
    MEDIA_IMAGE_SUFFIXES,
    TEMPLATE_REPOSITORY,
    Project,
    SiteConfig,
    discover_project_directories,
    load_project,
    load_site_config,
    read_frontmatter,
)
from .payload import collect_payload
from .problems import Problems
from .versions import Version

GENERATED_ROOT = Path("static") / "dreamweave"
VIEW_FILE = GENERATED_ROOT / "view.json"
INDEX_FILE = Path("static") / "dreamweave.json"
DIST = Path("dist")

# Everything an archive's bytes can depend on: the payload, and everything the offline documentation
# render reads. A stray note at the repository root is not one of them.
ARCHIVE_INPUTS = ("content", "templates", "sass", "static", "data", "config.toml", "tools", "buildSite")


@dataclass
class Repository:
    root: Path
    site: SiteConfig
    projects: list[Project]
    locks: dict[str, list[records.LockedRelease]]
    head: str
    problems: Problems = field(default_factory=Problems)

    def project_by_slug(self, slug: str) -> Project:
        for project in self.projects:
            if project.slug == slug:
                return project
        known = ", ".join(sorted(project.slug for project in self.projects)) or "none"
        raise SystemExit(f"No mod.toml project has slug {slug!r} (known: {known}).")

    def nested_directories(self, project: Project) -> list[str]:
        return [other.directory for other in self.projects if other.directory.startswith(f"{project.directory}/")]


def load_repository(root: Path, check_payloads: bool = True) -> Repository:
    problems = Problems()
    gitrepo.require_repository()
    site = load_site_config(root, problems)

    github_repository = os.environ.get("GITHUB_REPOSITORY")
    if github_repository and site.repository and github_repository.lower() != site.repository.lower():
        problems.error(
            "config.toml [extra]",
            f"github_username/github_project say {site.repository}, but this workflow is running in {github_repository}. "
            "Point them at the repository that publishes the site",
        )

    projects = []
    for directory in discover_project_directories(root):
        project = load_project(root, directory, problems)
        if project:
            records.check_openmw_runtime(project, problems)
            projects.append(project)

    seen_ids: dict[str, str] = {}
    seen_slugs: dict[str, str] = {}
    for project in projects:
        if project.id in seen_ids:
            problems.error(project.directory, f"id {project.id} is already used by {seen_ids[project.id]}")
        seen_ids[project.id] = project.directory
        if project.slug in seen_slugs:
            problems.error(project.directory, f"slug {project.slug!r} is already used by {seen_slugs[project.slug]}")
        seen_slugs[project.slug] = project.directory
        if project.id in EXAMPLE_PROJECT_IDS and site.repository.lower() != TEMPLATE_REPOSITORY.lower():
            problems.error(
                f"{project.directory}/mod.toml",
                f"id {project.id} belongs to the template's example project {EXAMPLE_PROJECT_IDS[project.id]}. "
                "Every project needs its own identity: replace it with the output of ./buildSite new-id",
            )
        for item in project.media:
            if item.file:
                check_media_file(root, project, item.file, problems)
            if item.thumbnail:
                check_media_file(root, project, item.thumbnail, problems)

    check_version_three_pages(root, projects, problems)
    head = gitrepo.resolve_revision("HEAD")
    locks = {project.id: records.read_lock(project, root, problems) for project in projects}
    for project in projects:
        check_release_order(project, locks[project.id], problems)

    repository = Repository(root=root, site=site, projects=projects, locks=locks, head=head, problems=problems)
    if check_payloads:
        for project in projects:
            collect_payload(project, None, repository.nested_directories(project), problems, root)
    return repository


def check_release_order(project: Project, locked: list[records.LockedRelease], problems: Problems) -> None:
    """Within a channel, a later release must sort higher, or clients pick the wrong update.

    Only releases that are or can still be published count: tags pushed before any lock existed
    are history that can never enter the manifest, so their order is not a client's problem.
    """
    locked_versions = {release.version for release in locked}
    publishable = [
        release for release in project.releases
        if release.version in locked_versions or gitrepo.tag_revision(project.release_tag(release.version)) is None
    ]
    by_channel: dict[str, list] = {}
    for release in publishable:
        by_channel.setdefault(release.channel, []).append(release)
    for channel, channel_releases in by_channel.items():
        ordered = sorted(channel_releases, key=lambda release: (release.date, release.version.precedence_key()))
        for earlier, later in zip(ordered, ordered[1:]):
            if later.version < earlier.version:
                hint = (
                    'If this project numbers releases like decimals (0.82 then 0.9), set versioning = "decimal"; otherwise pick a version that sorts after the last one'
                    if project.versioning == "numeric" else "Pick a version that sorts after the last one"
                )
                problems.error(
                    f"{project.directory}/mod.toml",
                    f"{channel} release {later.version} ({later.date}) sorts below {earlier.version} ({earlier.date}) under {project.versioning} versioning. {hint}",
                )


def check_version_three_pages(root: Path, projects: list[Project], problems: Problems) -> None:
    """V3 kept project metadata in the frontmatter of content/<project>/index.md. V4 does not read
    it, so it must not linger. V3 only ever treated direct children of content/ as projects."""
    project_directories = {root / project.directory for project in projects}
    for index in sorted((root / "content").glob("*/index.md")):
        if index.parent in project_directories:
            continue
        try:
            extra = (read_frontmatter(index) or {}).get("extra") or {}
        except Exception:
            continue
        stale = [key for key in ("version", "install_info", "nexus_id", "nexus_group_id", "offsite_host") if key in extra]
        if stale:
            problems.error(
                index.relative_to(root).as_posix(),
                f"has V3 project frontmatter ({', '.join(stale)}) but no mod.toml. V4 reads project metadata from mod.toml; "
                "see content/guide/migration.md, or keep building this site from the V3 tag",
            )


def check_media_file(root: Path, project: Project, file: str, problems: Problems) -> None:
    where = f"{project.directory}/mod.toml media {file!r}"
    if file.startswith("/") or ".." in file.split("/") or "\\" in file:
        problems.error(where, "must be a path inside the project directory, like media/combat.webp")
        return
    if not file.lower().endswith(MEDIA_IMAGE_SUFFIXES):
        problems.error(where, f"is not an image ({', '.join(MEDIA_IMAGE_SUFFIXES)})")
    if not (root / project.directory / file).is_file():
        problems.error(where, "does not exist")


@dataclass
class ReleaseState:
    published: list[records.PublishedRelease]
    pending: list[str]
    unlocked_tags: list[str]
    planned: list[str]


def release_state(repository: Repository, project: Project) -> ReleaseState:
    locked = {release.version: release for release in repository.locks[project.id]}
    published, pending, unlocked_tags, planned = [], [], [], []
    for declared in project.releases:
        tag = project.release_tag(declared.version)
        revision = gitrepo.tag_revision(tag)
        record = locked.get(declared.version)
        if record and revision:
            published.append(records.PublishedRelease(declared=declared, locked=record, tag=tag, revision=revision, channel=declared.channel, date=declared.date))
        elif record:
            pending.append(str(declared.version))
        elif revision:
            unlocked_tags.append(str(declared.version))
        else:
            planned.append(str(declared.version))
    return ReleaseState(published=published, pending=pending, unlocked_tags=unlocked_tags, planned=planned)


def development_version(repository: Repository, project: Project, state: ReleaseState) -> Version:
    """The newest tagged release, published or not, plus the commits since its tag.

    Tags without a lock still say what players may already have installed, so a development build
    must sort above them even though the manifest cannot list them.
    """
    tagged = [release.locked.version for release in state.published]
    tagged += [release.version for release in project.releases if str(release.version) in state.unlocked_tags]
    base = max(tagged, key=lambda version: version.precedence_key(), default=None)
    since = project.release_tag(base) if base is not None else None
    count = gitrepo.count_commits(repository.head, since, project.directory)
    if base is None:
        base = Version.parse("0.0.0" if project.versioning == "numeric" else "0", project.versioning)
    return base.next_development(count)


def archive_entries(repository: Repository, project: Project, version: Version, revision: str | None, documentation: dict[str, bytes]) -> tuple[list[ArchiveEntry], dict]:
    problems = Problems()
    payload = collect_payload(project, revision, repository.nested_directories(project), problems, repository.root)
    problems.raise_if_any()

    contents = gitrepo.read_blobs([file.blob for file in payload if file.blob])
    entries = [
        ArchiveEntry(path=file.path, executable=file.executable, content=contents[file.blob] if file.blob else file.disk_path.read_bytes())
        for file in payload
    ]
    layout: dict = {"release_document": "dreamweave.release.json"}

    semantics = records.release_semantics(project)
    entries.append(ArchiveEntry("dreamweave.release.json", False, records.payload_release_document(project, version, semantics)))
    if project.package_documentation:
        entries.extend(ArchiveEntry(path, False, data) for path, data in sorted(documentation.items()))
        layout["documentation"] = f"{offline.DOCUMENTATION_ROOT}/index.html"
    if project.package_format == "fomod":
        website = f"{repository.site.base_url}/{project.page_path}"
        entries.append(ArchiveEntry("fomod/info.xml", False, fomod.info_xml(project, version, website)))
        entries.append(ArchiveEntry("fomod/ModuleConfig.xml", False, fomod.module_config_xml(project)))
        layout["installer"] = "fomod/ModuleConfig.xml"
    return entries, layout


def build_archive(repository: Repository, project: Project, version: Version, revision: str | None, documentation: dict[str, bytes]) -> tuple[ArchiveResult, dict]:
    entries, layout = archive_entries(repository, project, version, revision, documentation)
    filename = records.archive_filename(project)
    result = write_archive(repository.root / DIST / filename, entries)
    artifact = {
        "id": project.package_format,
        "format": project.package_format,
        "filename": filename,
        "media_type": records.MEDIA_TYPE_ZIP,
        "size": result.size,
        "digests": {"sha256": result.sha256},
        "layout": layout,
    }
    return result, artifact


def render_documentation(repository: Repository, projects: list[Project], packaged_versions: dict[str, Version]) -> dict[str, dict[str, bytes]]:
    documented = [project for project in projects if project.package_documentation]
    if not documented:
        return {}
    offline.require_zola(pinned=False)
    write_view(repository, offline_mode=True, packaged_versions=packaged_versions)
    return offline.build_documentation(repository.root, repository.site.base_url, [project.page_path for project in documented])


def lock_release(repository: Repository, slug: str, version_text: str | None) -> Path:
    project = repository.project_by_slug(slug)
    locked_versions = {release.version for release in repository.locks[project.id]}
    candidates = [release for release in project.releases if release.version not in locked_versions]
    if version_text:
        wanted = Version.parse(version_text, project.versioning)
        candidates = [release for release in candidates if release.version == wanted]
        if not candidates:
            raise SystemExit(f"{project.slug} {wanted} is not an unlocked release in {project.directory}/mod.toml.")
    if not candidates:
        raise SystemExit(f"Every release in {project.directory}/mod.toml is already locked. Add a [[releases]] entry for the new version first.")
    release = max(candidates, key=lambda candidate: candidate.version.precedence_key())

    tag = project.release_tag(release.version)
    if gitrepo.tag_revision(tag):
        raise SystemExit(
            f"Tag {tag} already exists, so {release.version} was published before it was locked. Its archive came from "
            "whatever built it then; rebuilding now would record a hash that does not match the published file."
        )
    dirty = gitrepo.dirty_paths([path for path in ARCHIVE_INPUTS if (repository.root / path).exists()])
    if dirty:
        listing = "\n  ".join(dirty[:20])
        raise SystemExit(f"Commit or stash your changes first. The lock records what is committed, and these are not:\n  {listing}")
    if project.package_documentation:
        offline.require_zola(pinned=True)

    documentation = render_documentation(repository, [project], {project.id: release.version})
    result, artifact = build_archive(repository, project, release.version, repository.head, documentation.get(project.page_path, {}))
    locked = records.LockedRelease(version=release.version, locked_from=repository.head, artifacts=[artifact], semantics=records.release_semantics(project))
    path = records.write_lock(project, repository.root, [*repository.locks[project.id], locked])
    print(f"Locked {project.slug} {release.version}: {artifact['filename']} {result.size} bytes sha256 {result.sha256}")
    print(f"Next: git add {path.relative_to(repository.root)} && git commit -m 'RELEASE: {project.name} {release.version}' && git tag {tag} && git push --atomic origin HEAD {tag}")
    return path


def verify_tag(repository: Repository, tag: str) -> list[Path]:
    """CI, on a tag: rebuild the release and refuse to publish unless it matches mod.lock."""
    slug, separator, version_text = tag.partition("-")
    if not separator:
        raise SystemExit(f"Tag {tag!r} is not <slug>-<version>.")
    project = repository.project_by_slug(slug)
    version = Version.parse(version_text, project.versioning)
    record = next((release for release in repository.locks[project.id] if release.version == version), None)
    if record is None:
        raise SystemExit(f"{project.directory}/mod.lock has no record for {version}. Run ./buildSite lock {slug} before tagging.")

    revision = gitrepo.resolve_revision(f"refs/tags/{tag}")
    if revision != repository.head:
        raise SystemExit(f"Check out {tag} before verifying it; HEAD is {repository.head[:12]}, the tag is {revision[:12]}.")
    if project.package_documentation:
        offline.require_zola(pinned=True)

    documentation = render_documentation(repository, [project], {project.id: version})
    result, artifact = build_archive(repository, project, version, revision, documentation.get(project.page_path, {}))
    expected = next(item for item in record.artifacts if item["id"] == artifact["id"])
    if expected["digests"]["sha256"] != result.sha256 or expected["size"] != result.size:
        raise SystemExit(
            f"{tag} does not reproduce its lock.\n"
            f"  mod.lock: {expected['size']} bytes sha256 {expected['digests']['sha256']}\n"
            f"  rebuilt:  {result.size} bytes sha256 {result.sha256}\n"
            "Something committed after `./buildSite lock` changed the archive (payload, documentation, templates or "
            "mod.toml). Delete the tag, run ./buildSite lock again, commit, and re-tag."
        )
    semantics = records.release_semantics(project)
    if semantics != record.semantics:
        raise SystemExit(f"{tag}: mod.toml's install or compatibility data changed after the lock was written. Re-run ./buildSite lock.")
    print(f"{tag} reproduces mod.lock: {result.size} bytes sha256 {result.sha256}")
    write_nexus_uploads(repository, project, version, artifact)
    write_release_notes(repository, project, version, artifact)
    write_signing_list(repository, [(project, artifact)])
    return [result.path]


def build_development(repository: Repository, include_archives: bool) -> dict[str, dict]:
    """Package every project's development build. Returns artifacts keyed by project id."""
    targets = [project for project in repository.projects if project.package_development]
    versions = {project.id: development_version(repository, project, release_state(repository, project)) for project in targets}
    artifacts: dict[str, dict] = {}
    if not include_archives or not targets:
        return artifacts

    documentation = render_documentation(repository, targets, versions)
    built = []
    for project in targets:
        result, artifact = build_archive(repository, project, versions[project.id], None, documentation.get(project.page_path, {}))
        artifacts[project.id] = artifact
        built.append((project, artifact))
        print(f"Built {project.slug} {versions[project.id]}: {result.size} bytes sha256 {result.sha256}")
    write_signing_list(repository, built)
    return artifacts


def write_release_notes(repository: Repository, project: Project, version: Version, artifact: dict) -> Path:
    """dist/release-notes.md: the GitHub Release body, from the same notes as the changelog."""
    declared = project.declared_release(version)
    notes = records.notes_document(declared)
    lines = [f"## {project.name} {version}", ""]
    if "summary" in notes:
        lines += [notes["summary"], ""]
    if "highlights" in notes:
        lines += [notes["highlights"], ""]
    for key, heading in (("breaking", "Breaking changes"), ("added", "Added"), ("changed", "Changed"), ("fixed", "Fixed"), ("known_issues", "Known issues")):
        if key in notes:
            lines += [f"### {heading}", "", *(f"- {line}" for line in notes[key]), ""]
    if "migration" in notes:
        lines += ["### Migration", "", notes["migration"], ""]
    if "notes" in notes:
        lines += [notes["notes"], ""]
    base_url = site_base_url(repository)
    lines += [
        "---",
        "",
        f"`{artifact['filename']}` · {artifact['size']} bytes · SHA-256 `{artifact['digests']['sha256']}`",
        "",
        f"Project page: {base_url}/{project.page_path} · Manifest: {base_url}/dreamweave/projects/{project.id}.json",
    ]
    path = repository.root / DIST / "release-notes.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_signing_list(repository: Repository, built: list[tuple[Project, dict]]) -> Path:
    """dist/sign.txt: archives whose projects asked for Sigstore signatures, one file name per line."""
    names = [artifact["filename"] for project, artifact in built if project.sigstore]
    path = repository.root / DIST / "sign.txt"
    path.write_text("".join(f"{name}\n" for name in names), encoding="utf-8")
    return path


def write_nexus_uploads(repository: Repository, project: Project, version: Version, artifact: dict) -> None:
    """dist/nexus.json: the Nexus Mods upload matrix for the workflow. Empty when nothing is configured."""
    uploads = []
    if project.nexusmods_file_group_id is not None:
        uploads.append({
            "name": project.name,
            "version": str(version),
            "file_group_id": project.nexusmods_file_group_id,
            "filename": artifact["filename"],
        })
    path = repository.root / DIST / "nexus.json"
    path.write_text(json.dumps(uploads), encoding="utf-8")


def write_changelog_stubs(repository: Repository) -> None:
    for project in repository.projects:
        path = repository.root / project.directory / "_changelog.md"
        path.write_text(
            f'+++\ntitle = {json.dumps(project.name + " changelog")}\nslug = "changelog"\ntemplate = "mod/changelog.html"\n\n[extra]\nproject = {json.dumps(project.page_path)}\n+++\n',
            encoding="utf-8",
        )


def site_base_url(repository: Repository) -> str:
    return (os.environ.get("DREAMWEAVE_BASE_URL") or repository.site.base_url).rstrip("/")


def write_site(repository: Repository, development_artifacts: dict[str, dict], archives_built: bool) -> None:
    """Write the public protocol documents and the data the templates render from."""
    root = repository.root
    base_url = site_base_url(repository)
    generated = root / GENERATED_ROOT
    projects_directory = generated / "projects"
    projects_directory.mkdir(parents=True, exist_ok=True)
    for stale in projects_directory.glob("*.json"):
        stale.unlink()

    index_entries = []
    for project in repository.projects:
        state = release_state(repository, project)
        releases = [
            records.release_document(project, repository.site, release, release.tag, f"refs/tags/{release.tag}")
            for release in state.published
        ]
        if project.package_development and project.id in development_artifacts:
            version = development_version(repository, project, state)
            locked = records.LockedRelease(version=version, locked_from=repository.head, artifacts=[development_artifacts[project.id]], semantics=records.release_semantics(project))
            development = records.PublishedRelease(declared=None, locked=locked, tag="development", revision=repository.head, channel=DEVELOPMENT_CHANNEL, date=gitrepo.commit_time(repository.head)[:10])
            releases.append(records.release_document(project, repository.site, development, "development", os.environ.get("DREAMWEAVE_DEVELOPMENT_REF", "refs/heads/main")))

        manifest = records.project_manifest(project, repository.site, base_url, releases)
        manifest_text = records.dumps(manifest)
        (projects_directory / f"{project.id}.json").write_text(manifest_text, encoding="utf-8")
        index_entries.append({
            "id": project.id,
            "name": project.name,
            **({"summary": project.summary} if project.summary else {}),
            "type": project.type,
            "status": project.status,
            "page": f"{base_url}/{project.page_path}",
            "manifest": f"{base_url}/dreamweave/projects/{project.id}.json",
            "manifest_sha256": hashlib.sha256(manifest_text.encode("utf-8")).hexdigest(),
            "updated": max((release["date"] for release in releases if "date" in release), default=None),
            "channels": {channel: head["version"] for channel, head in manifest["channels"].items()},
        })

    (root / INDEX_FILE).write_text(records.dumps(records.site_index(repository.site, base_url, index_entries)), encoding="utf-8")
    write_view(repository, offline_mode=False, archives_built=archives_built)


def write_view(repository: Repository, offline_mode: bool, packaged_versions: dict[str, Version] | None = None, archives_built: bool = True) -> None:
    from .view import build_view

    root = repository.root
    base_url = site_base_url(repository)
    view = build_view(repository, base_url, offline_mode, packaged_versions or {}, archives_built)
    path = root / VIEW_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(records.dumps(view), encoding="utf-8")


def clean_dist(root: Path) -> None:
    dist = root / DIST
    if dist.exists():
        for item in dist.iterdir():
            if item.is_file():
                item.unlink()
