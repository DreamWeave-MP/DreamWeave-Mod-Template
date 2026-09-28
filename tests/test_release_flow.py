"""The release lifecycle end to end, in a throwaway repository built from this template."""

import hashlib
import json
import re
import shutil
import subprocess
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from support import LANTERN, LANTERN_FILES, REPOSITORY, Scratch, build_site, git

try:
    import jsonschema
except ImportError:
    jsonschema = None

LANTERN_ID = "0b8f1c2d-3e4a-4b5c-8d6e-7f8091a2b3c4"
HAS_ZOLA = shutil.which("zola") is not None


def load(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text())


def schema_errors(document: dict, schema_name: str) -> list[str]:
    schema = json.loads((REPOSITORY / "static/schemas" / schema_name).read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{list(error.path)}: {error.message}" for error in validator.iter_errors(document)]


@unittest.skipUnless(HAS_ZOLA, "Zola renders the documentation inside archives")
class ReleaseLifecycle(unittest.TestCase):
    def setUp(self):
        self.scratch = Scratch()
        self.root = self.scratch.root
        self.scratch.add_project("lantern", LANTERN, files=LANTERN_FILES)
        self.scratch.commit("Add Lantern")

    def tearDown(self):
        self.scratch.cleanup()

    def manifest(self) -> dict:
        return load(self.root, f"static/dreamweave/projects/{LANTERN_ID}.json")

    def lock_and_tag(self, version: str = "1.0.0") -> str:
        build_site(self.root, "lock", "lantern", "--version", version)
        revision = self.scratch.commit(f"RELEASE: Lantern {version}")
        git(self.root, "tag", f"lantern-{version}")
        return revision

    def test_before_any_release_only_the_development_channel_exists(self):
        build_site(self.root, "build")
        manifest = self.manifest()
        self.assertEqual(list(manifest["channels"]), ["development"])
        development = manifest["releases"][0]
        self.assertEqual(development["channel"], "development")
        self.assertRegex(development["version"], r"^0\.0\.1-dev\.\d+$")
        artifact = development["artifacts"][0]
        self.assertEqual(artifact["sources"][0]["url"], "https://github.com/someone/cool-mods/releases/download/development/lantern.zip")
        self.assertEqual(artifact["digests"]["sha256"], hashlib.sha256((self.root / "dist/lantern.zip").read_bytes()).hexdigest())

    def test_lock_tag_verify_publish(self):
        revision = self.lock_and_tag()
        lock = load(self.root, "content/lantern/mod.lock")
        self.assertEqual(lock["project"], LANTERN_ID)
        locked = lock["releases"][0]
        self.assertEqual(locked["version"], "1.0.0")

        git(self.root, "checkout", "-q", "lantern-1.0.0")
        output = build_site(self.root, "verify", "lantern-1.0.0").stdout
        self.assertIn("reproduces mod.lock", output)
        rebuilt = hashlib.sha256((self.root / "dist/lantern.zip").read_bytes()).hexdigest()
        self.assertEqual(rebuilt, locked["artifacts"][0]["digests"]["sha256"])
        git(self.root, "checkout", "-q", "main")

        build_site(self.root, "build")
        manifest = self.manifest()
        self.assertEqual(manifest["channels"]["stable"], {"version": "1.0.0"})
        stable = next(release for release in manifest["releases"] if release["version"] == "1.0.0")
        self.assertEqual(stable["status"], "available")
        self.assertEqual(stable["source"]["revision"], revision)
        self.assertEqual(stable["source"]["tag"], "lantern-1.0.0")
        self.assertEqual(stable["artifacts"][0]["digests"], locked["artifacts"][0]["digests"])
        self.assertEqual(stable["artifacts"][0]["sources"][0]["url"], "https://github.com/someone/cool-mods/releases/download/lantern-1.0.0/lantern.zip")
        self.assertEqual(stable["notes"]["summary"], "First.")
        development = next(release for release in manifest["releases"] if release["channel"] == "development")
        self.assertRegex(development["version"], r"^1\.0\.1-dev\.\d+$")

        if jsonschema:
            self.assertEqual(schema_errors(manifest, "modManifest-2.schema.json"), [])
            self.assertEqual(schema_errors(load(self.root, "static/dreamweave.json"), "dreamweave-index-2.schema.json"), [])

    def test_a_tag_that_does_not_reproduce_its_lock_is_refused(self):
        build_site(self.root, "lock", "lantern")
        self.scratch.commit("RELEASE: Lantern 1.0.0")
        self.scratch.write("content/lantern/scripts/lantern/player.lua", "return { changed = true }\n")
        self.scratch.commit("Sneak a change in after locking")
        git(self.root, "tag", "lantern-1.0.0")
        process = build_site(self.root, "verify", "lantern-1.0.0", check=False)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("does not reproduce its lock", process.stdout + process.stderr)

    def test_lock_refuses_uncommitted_work_and_published_tags(self):
        self.scratch.write("content/lantern/scripts/lantern/extra.lua", "return {}\n")
        process = build_site(self.root, "lock", "lantern", check=False)
        self.assertIn("Commit or stash your changes first", process.stdout + process.stderr)

        (self.root / "content/lantern/scripts/lantern/extra.lua").unlink()
        git(self.root, "tag", "lantern-1.0.0")
        process = build_site(self.root, "lock", "lantern", check=False)
        self.assertIn("already exists", process.stdout + process.stderr)

    def test_packaging_is_byte_reproducible(self):
        build_site(self.root, "build")
        first = (self.root / "dist/lantern.zip").read_bytes()
        shutil.rmtree(self.root / "dist")
        build_site(self.root, "build")
        self.assertEqual(first, (self.root / "dist/lantern.zip").read_bytes())

    def test_yanked_releases_stay_listed_but_leave_the_channel(self):
        self.lock_and_tag("1.0.0")
        mod_toml = (self.root / "content/lantern/mod.toml").read_text()
        (self.root / "content/lantern/mod.toml").write_text(mod_toml + '\n[[releases]]\nversion = "1.1.0"\ndate = 2026-02-01\n')
        self.scratch.commit("Declare 1.1.0")
        self.lock_and_tag("1.1.0")
        mod_toml = (self.root / "content/lantern/mod.toml").read_text()
        (self.root / "content/lantern/mod.toml").write_text(mod_toml.replace('version = "1.1.0"\n', 'version = "1.1.0"\nyanked = "Deletes saves."\nreplacement = "1.0.0"\n'))
        self.scratch.commit("Yank 1.1.0")

        build_site(self.root, "build")
        manifest = self.manifest()
        yanked = next(release for release in manifest["releases"] if release["version"] == "1.1.0")
        self.assertEqual(yanked["status"], "yanked")
        self.assertEqual(yanked["yanked"], {"reason": "Deletes saves.", "replacement": "1.0.0"})
        self.assertEqual(manifest["channels"]["stable"], {"version": "1.0.0"})

    def test_archive_contents(self):
        build_site(self.root, "build")
        archive = zipfile.ZipFile(self.root / "dist/lantern.zip")
        names = set(archive.namelist())
        for expected in ("Lantern.omwscripts", "scripts/lantern/player.lua", "index.md", "mod.toml", "dreamweave.release.json", "Documentation/index.html"):
            self.assertIn(expected, names)
        self.assertNotIn("mod.lock", names)
        self.assertFalse(any(name.startswith("_changelog") for name in names))

        release = json.loads(archive.read("dreamweave.release.json"))
        self.assertEqual(release["project"]["id"], LANTERN_ID)
        if jsonschema:
            self.assertEqual(schema_errors(release, "dreamweave-release-payload-2.schema.json"), [])

        page = archive.read("Documentation/index.html").decode()
        project_links = re.findall(r'(?:href|src)="https://example\.github\.io/cool-mods/lantern/[^"]*"', page)
        self.assertEqual(len(project_links), 1, f"only the offline banner's live-page link may stay absolute: {project_links}")
        self.assertIn('data-dw-online', page)
        self.assertIn('href="changelog/index.html"', page)
        for reference in re.findall(r'(?:href|src)="(_site/[^"#]+)"', page):
            self.assertIn(f"Documentation/{reference}", names, f"offline page references a file the archive lacks: {reference}")
        for info in archive.infolist():
            self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
            self.assertEqual(info.compress_type, zipfile.ZIP_STORED)

    def test_fomod_installer_matches_the_component_model(self):
        self.scratch.add_project("hearth", """
            id = "5c6d7e8f-9a0b-4c1d-8e2f-3a4b5c6d7e8f"
            slug = "hearth"

            [runtimes]
            openmw = "*"

            [package]
            format = "fomod"

            [[components]]
            id = "core"
            name = "Core"
            path = "00 Core"
            required = true

            [components.openmw]
            content_files = ["Hearth.omwscripts"]

            [[groups]]
            id = "smoke"
            name = "Smoke & <sparks>"
            select = "exactly-one"

            [[components]]
            id = "light-smoke"
            name = "Light smoke"
            path = "10 Light"
            group = "smoke"
            default = true

            [[components]]
            id = "heavy-smoke"
            name = "Heavy smoke"
            path = "11 Heavy"
            group = "smoke"
        """, title="Hearth", files={"00 Core/Hearth.omwscripts": "PLAYER: x.lua\n", "10 Light/a.txt": "a", "11 Heavy/b.txt": "b"})
        self.scratch.commit("Add Hearth")
        build_site(self.root, "build")
        archive = zipfile.ZipFile(self.root / "dist/hearth.zip")
        config = ElementTree.fromstring(archive.read("fomod/ModuleConfig.xml"))
        self.assertEqual(config.findtext("moduleName"), "Hearth")
        self.assertEqual([folder.get("source") for folder in config.find("requiredInstallFiles")], ["00 Core"])
        group = config.find(".//group")
        self.assertEqual(group.get("name"), "Smoke & <sparks>")
        self.assertEqual(group.get("type"), "SelectExactlyOne")
        types = {plugin.get("name"): plugin.find(".//type").get("name") for plugin in group.iter("plugin")}
        self.assertEqual(types, {"Light smoke": "Recommended", "Heavy smoke": "Optional"})
        ElementTree.fromstring(archive.read("fomod/info.xml"))

    def test_rendered_site_advertises_discovery_under_a_subdirectory(self):
        build_site(self.root, "build")
        subprocess.run(["zola", "build"], cwd=self.root, check=True, capture_output=True)
        page = (self.root / "public/lantern/index.html").read_text()
        self.assertIn('type="application/vnd.dreamweave.index+json" title="DreamWeave index" href="https://example.github.io/cool-mods/dreamweave.json"', page)
        self.assertIn(f'href="https://example.github.io/cool-mods/dreamweave/projects/{LANTERN_ID}.json"', page)
        self.assertTrue((self.root / "public/dreamweave.json").is_file())
        self.assertTrue((self.root / f"public/dreamweave/projects/{LANTERN_ID}.json").is_file())
        self.assertFalse((self.root / "public/lantern/mod.toml").exists(), "mod.toml is a build input, not a published file")
        index = load(self.root, "public/dreamweave.json")
        self.assertEqual(index["projects"][0]["manifest"], f"https://example.github.io/cool-mods/dreamweave/projects/{LANTERN_ID}.json")
        self.assertEqual(index["projects"][0]["manifest_sha256"], hashlib.sha256((self.root / f"public/dreamweave/projects/{LANTERN_ID}.json").read_bytes()).hexdigest())

    def test_author_text_is_escaped(self):
        hostile = '</script><script>alert(1)</script>'
        index = (self.root / "content/lantern/index.md").read_text().replace('title = "Lantern"', f"title = '{hostile}'")
        (self.root / "content/lantern/index.md").write_text(index)
        mod_toml = (self.root / "content/lantern/mod.toml").read_text().replace('summary = "First."', 'summary = "<img src=x onerror=alert(2)>"')
        (self.root / "content/lantern/mod.toml").write_text(mod_toml)
        self.scratch.commit("Hostile text")
        build_site(self.root, "build")
        subprocess.run(["zola", "build"], cwd=self.root, check=True, capture_output=True)
        page = (self.root / "public/lantern/index.html").read_text()
        self.assertNotIn("<script>alert(1)", page)
        self.assertNotIn("<img src=x onerror", page)
        install_model = re.search(r'<script type="application/json" data-install-model>(.*?)</script>', page, re.S).group(1)
        self.assertNotIn("<", install_model)
        self.assertEqual(json.loads(install_model)["name"], hostile)


if __name__ == "__main__":
    unittest.main()
