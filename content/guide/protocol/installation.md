+++
title = "Installation"
description = "Components, groups, the OpenMW extension, and installing without scripts."
weight = 50

[extra]
kind = "reference"
+++

Installation is declarative. A manifest says which directories are data, which files are content,
which settings are needed; a client that understands those statements performs them. Nothing in a
manifest is executed. An installer that needs to run code is a different protocol with a different
security model, and it will not arrive as a field here.

## Components

```json
{ "id": "core", "name": "Core", "path": "00 Core", "required": true, "default": true,
  "requires": [], "conflicts": [], "suggested_with": [] }
```

| Field | Meaning |
|---|---|
| `id` | Token, unique within the release. |
| `path` | Directory inside the archive, or `.` for its root. Forward slashes, no `.` or `..` segments. |
| `required` | Always installed. |
| `default` | Selected unless the user chooses otherwise. |
| `group` | *Optional.* A group id this component is one choice in. |
| `requires`, `conflicts` | Component ids of the same release. |
| `suggested_with` | Project ids. A client SHOULD pre-select the component when one of them is installed. |

Groups:

```json
{ "id": "flames", "name": "Flame textures", "select": "exactly-one" }
```

`select` is `exactly-one`, `at-most-one`, `at-least-one` or `any`, constraining how many of the
group's members may be selected.

A selection is valid when it contains every required component, satisfies every group, contains the
`requires` of every selected component and none of their `conflicts`. A client MUST NOT install an
invalid selection. The publisher's tooling rejects releases for which no valid selection exists.

`format` says how components sit in the archive: `flat` has one component at `.`; `bain` and `fomod`
have one top-level directory per component.

## The OpenMW extension

When a release's `runtimes` includes `openmw`, its `extensions.openmw` says how to install it into
OpenMW, and `critical_extensions` contains `"openmw"`.

```json
"openmw": {
  "lua_api": ">=60",
  "requires_content": ["Morrowind.esm"],
  "settings": [{ "category": "Shaders", "key": "force per pixel lighting", "value": "true" }],
  "components": {
    "core": {
      "data_directories": ["."],
      "content_files": ["Candlelight.omwscripts"],
      "groundcover_files": [],
      "fallback_archives": [],
      "fallback_entries": {},
      "config": false,
      "requires_content": []
    }
  }
}
```

For each selected component, in the order `components` lists them, with `R` the directory the
component's `path` was extracted to:

| Field | `openmw.cfg` |
|---|---|
| `data_directories` | `data="R/<dir>"` for each, in order (`.` is `R` itself) |
| `fallback_archives` | `fallback-archive=<name>` for each |
| `content_files` | `content=<name>` for each, in order; this is load order |
| `groundcover_files` | `groundcover=<name>` for each |
| `fallback_entries` | `fallback=<key>,<value>` for each |
| `config` | `config="R"`: the component ships its own `openmw.cfg` |

Every named file exists in one of the component's data directories, with that exact case; the
publisher's tooling checks this before release. `requires_content`, at either level, names content
files that must already be active. `lua_api` constrains `core.API_REVISION`. `settings` are values
the user's `settings.cfg` needs; a client SHOULD show them and MAY apply them with the user's
consent. `data=` lines of a project SHOULD come after those of the projects it `requires`.

## Other installers

A `fomod` archive's installer is generated from these same components, so MO2 and Vortex make the
same choices a DreamWeave client would. A client that does not implement the OpenMW extension may
still download and verify a release, but because `openmw` is critical, it MUST NOT report the
release as installed.
