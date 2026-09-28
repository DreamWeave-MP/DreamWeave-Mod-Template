"""static/dreamweave/view.json: what the templates render.

Built from the same records as the published manifests, so a page cannot claim something the
manifest does not. In offline mode (documentation inside archives) it holds only what the
committed tree says, never mod.lock, git state or the clock.
"""

import hashlib
import json

from . import records
from .build import GENERATED_ROOT, INDEX_FILE, Repository, release_state
from .model import Project
from .payload import collect_payload, join, undeclared_content_files
from .problems import Problems
from .versions import Version

INSTALL_PATH_PLACEHOLDER = "C:/Games/OpenMW-Mods"


def json_for_script(value: object) -> str:
    """JSON that is safe inside <script type="application/json">, whatever authors wrote."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def relationship_views(repository: Repository, project: Project) -> dict:
    by_id = {other.id: other for other in repository.projects}
    grouped: dict[str, list] = {kind: [] for kind in ("requires", "recommends", "conflicts", "compatible", "replaces")}
    for relationship in project.relationships:
        local = by_id.get(relationship.project_id) if relationship.project_id else None
        grouped[relationship.kind].append({
            **records.relationship_document(relationship),
            "display_name": relationship.name or (local.name if local else None) or relationship.capability or relationship.project_id,
            **({"page_path": local.page_path} if local else {}),
        })
    for other in repository.projects:
        for relationship in other.relationships:
            if relationship.project_id == project.id and relationship.kind in ("requires", "recommends"):
                grouped.setdefault("required_by" if relationship.kind == "requires" else "recommended_by", []).append({
                    "project": other.id, "display_name": other.name, "page_path": other.page_path,
                    **({"version": str(relationship.version)} if relationship.version else {}),
                })
    return grouped


def config_lines(project: Project, install_root: str) -> list[dict]:
    """openmw.cfg lines per component, for the install panel. The install path is a placeholder."""
    lines = []
    for component in project.components:
        openmw = component.openmw
        entries = []
        for key, value in sorted(openmw.fallback_entries.items()):
            entries.append(f"fallback={key},{value}")
        for directory in openmw.data_directories:
            path = join(component.path, directory)
            entries.append(f'data="{install_root}' + ("" if path == "." else f"/{path}") + '"')
        entries.extend(f"fallback-archive={name}" for name in openmw.fallback_archives)
        entries.extend(f"content={name}" for name in openmw.content_files)
        entries.extend(f"groundcover={name}" for name in openmw.groundcover_files)
        if openmw.config:
            entries.append(f'config="{install_root}' + ("" if component.path == "." else f"/{component.path}") + '"')
        lines.append({"component": component.id, "lines": entries})
    return lines


def declared_release_views(project: Project, state, offline_mode: bool, packaged: Version | None) -> list[dict]:
    published = {str(release.locked.version) for release in state.published}
    packaging_declared_release = packaged is not None and any(release.version == packaged for release in project.releases)
    views = []
    for release in sorted(project.releases, key=lambda release: release.version.precedence_key(), reverse=True):
        if offline_mode and packaging_declared_release and release.version > packaged:
            continue
        view: dict = {
            "version": str(release.version),
            "channel": release.channel,
            "date": release.date,
            "notes": records.notes_document(release),
        }
        if release.yanked:
            view["yanked"] = release.yanked
        if release.deprecated:
            view["deprecated"] = release.deprecated
        if release.replacement:
            view["replacement"] = str(release.replacement)
        if not offline_mode:
            version = str(release.version)
            view["state"] = (
                "published" if version in published
                else "pending" if version in state.pending
                else "unverified" if version in state.unlocked_tags
                else "planned"
            )
        views.append(view)
    return views


def diagnostic_checks(repository: Repository, project: Project, state, manifest: dict, archives_built: bool) -> list[dict]:
    checks = []

    def check(identifier: str, label: str, status: str, detail: str) -> None:
        checks.append({"id": identifier, "label": label, "state": status, "detail": detail})

    check("identity", "Stable identity", "pass", f"id {project.id}; survives renames and host moves")
    check("discovery", "Discovery", "pass", "listed in dreamweave.json and linked from every page with <link rel=\"alternate\">")
    check("manifest", "Manifest", "pass", f"schema_version {manifest['schema_version']}, {len(manifest['releases'])} release(s) published")

    stable = [release for release in state.published]
    if stable:
        check("releases", "Published releases", "pass", ", ".join(str(release.locked.version) for release in stable))
    else:
        check("releases", "Published releases", "warn", "nothing is locked and tagged yet; clients only see the development channel")
    if state.pending:
        check("pending", "Locked, not tagged", "info", f"{', '.join(state.pending)}: push the tag to publish")
    if state.unlocked_tags:
        check("unverified", "Tagged without a lock", "warn", f"{', '.join(state.unlocked_tags)}: published before DreamWeave 4 or without ./buildSite lock; excluded from the manifest because nothing records their hashes")
    if state.planned:
        check("planned", "Declared, not locked", "info", ", ".join(state.planned))

    channels = manifest["channels"]
    if channels:
        check("channels", "Channels", "pass", ", ".join(f"{channel} → {head['version']}" for channel, head in channels.items()))
    elif project.package_development and not archives_built:
        check("channels", "Channels", "info", "the development channel appears once ./buildSite build packages it")
    else:
        check("channels", "Channels", "fail", "no channel has an available release")

    missing_digests = [
        f"{release['version']} {artifact['id']}"
        for release in manifest["releases"] for artifact in release["artifacts"]
        if "sha256" not in artifact.get("digests", {})
    ]
    if project.package_development and not archives_built:
        check("hashes", "Content hashes", "info", "development archives were not built in this preview; ./buildSite build computes them")
    elif missing_digests:
        check("hashes", "Content hashes", "fail", f"missing for {', '.join(missing_digests)}")
    else:
        check("hashes", "Content hashes", "pass", "every published artifact has a SHA-256 digest and size")

    identified = [relationship for relationship in project.relationships if relationship.project_id or relationship.capability]
    unidentified = [relationship for relationship in project.relationships if not relationship.project_id and not relationship.capability]
    if unidentified:
        names = ", ".join(relationship.name for relationship in unidentified if relationship.name)
        check("relationships", "Relationships", "info", f"{len(identified)} machine-resolvable; {names} named for humans only (no id)")
    elif project.relationships:
        check("relationships", "Relationships", "pass", f"{len(identified)} machine-resolvable")
    else:
        check("relationships", "Relationships", "info", "none declared")

    if project.sigstore:
        check("provenance", "Signatures", "pass", "CI signs each archive with Sigstore (keyless, tied to this repository's workflow)")
    else:
        check("provenance", "Signatures", "info", "not signed; hashes still verify integrity. Set [provenance] sigstore = true to add build provenance")

    revisions = [release for release in state.published if release.revision]
    check("source", "Source revisions", "pass" if revisions or not state.published else "warn", f"{len(revisions)} of {len(state.published)} published releases map to a commit")
    check("mirrors", "Mirrors", "info" if not project.mirrors else "pass", f"{len(project.mirrors)} configured; every artifact also has its publisher source")

    problems = Problems()
    payload = collect_payload(project, None, repository.nested_directories(project), problems, repository.root)
    undeclared = undeclared_content_files(project, payload)
    if undeclared:
        check("content", "Content files", "info", f"not declared in openmw.content_files: {', '.join(undeclared)}")
    return checks


def project_view(repository: Repository, project: Project, base_url: str, offline_mode: bool, packaged: Version | None, archives_built: bool) -> dict:
    state = release_state(repository, project)
    semantics = records.release_semantics(project)
    view: dict = {
        "id": project.id,
        "slug": project.slug,
        "name": project.name,
        "summary": project.summary,
        "type": project.type,
        "status": project.status,
        "game": project.game,
        "license": project.license,
        "tags": project.tags,
        "page_path": project.page_path,
        "format": project.package_format,
        "documentation_packaged": project.package_documentation,
        "maintainers": [{"name": person.name, "url": person.url} for person in project.maintainers],
        "links": records.project_links(project, repository.site, repository.site.base_url if offline_mode else base_url),
        "nexusmods": {"game": project.game, "mod_id": project.nexusmods_mod_id} if project.nexusmods_mod_id is not None else None,
        "media": [
            {"kind": item.kind, "file": item.file, "url": item.url, "alt": item.alt, "caption": item.caption,
             "category": item.category, "featured": item.featured, "thumbnail": item.thumbnail}
            for item in project.media
        ],
        "credits": [{"name": credit.name, "role": credit.role, "url": credit.url} for credit in project.credits],
        "runtimes": semantics["runtimes"],
        "platforms": semantics["platforms"],
        "provides": semantics["provides"],
        "relationships": relationship_views(repository, project),
        "components": semantics["components"],
        "groups": semantics["groups"],
        "implicit_component": project.implicit_component,
        "openmw": semantics["extensions"].get("openmw"),
        "install_notes": project.install_notes,
        "install_data": json_for_script({
            "slug": project.slug,
            "name": project.name,
            "placeholder": INSTALL_PATH_PLACEHOLDER,
            "components": [
                {"id": component.id, "required": component.required, "default": component.default, "group": component.group}
                for component in project.components
            ],
            "config": config_lines(project, "{install}"),
        }),
        "config_preview": config_lines(project, f"{INSTALL_PATH_PLACEHOLDER}/{project.name}"),
        "declared_releases": declared_release_views(project, state, offline_mode, packaged),
    }

    if offline_mode:
        view["packaged_version"] = str(packaged) if packaged else None
        return view

    manifest_path = repository.root / GENERATED_ROOT / "projects" / f"{project.id}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else None
    view["manifest_url"] = f"{base_url}/dreamweave/projects/{project.id}.json"
    if manifest is None:
        return view

    view["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    view["channels"] = manifest["channels"]
    channels = list(manifest["channels"])
    view["channel_order"] = [channel for channel in ("stable",) if channel in channels] + sorted(
        channel for channel in channels if channel not in ("stable", "development")
    ) + [channel for channel in ("development",) if channel in channels]
    view["releases"] = manifest["releases"]
    heads = {}
    for channel, head in manifest["channels"].items():
        release = next(release for release in manifest["releases"] if release["version"] == head["version"] and release["channel"] == channel)
        heads[channel] = release
    view["heads"] = heads
    view["checks"] = diagnostic_checks(repository, project, state, manifest, archives_built)
    return view


def build_view(repository: Repository, base_url: str, offline_mode: bool, packaged_versions: dict[str, Version], archives_built: bool) -> dict:
    projects = {
        project.page_path: project_view(repository, project, base_url, offline_mode, packaged_versions.get(project.id), archives_built)
        for project in repository.projects
    }
    view: dict = {
        "offline": offline_mode,
        "generator": records.GENERATOR,
        "schema_version": records.SCHEMA_VERSION,
        "projects": projects,
        "order": [project.page_path for project in sorted(repository.projects, key=lambda project: project.name.casefold())],
    }
    if offline_mode:
        return view

    view["index_url"] = f"{base_url}/{INDEX_FILE.name}"
    view["comments"] = repository.comments()
    view["archives_built"] = archives_built
    view["revision"] = repository.head
    return view
