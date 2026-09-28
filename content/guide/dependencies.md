+++
title = "Dependencies"
description = "Requirements, integrations, conflicts, capabilities, and the constraint grammar."
weight = 50

[extra]
kind = "guide"
+++

"Requires Tallow 1.0+" means something different to every reader. Here it means one thing, written
so a client can act on it:

```toml
[[requires]]
id = "9b7e3f21-6c4d-4a8b-b1e2-3f5a7c9d0e14"
name = "Tallow"
version = ">=1.0"
url = "https://dreamweave-mp.github.io/DreamWeave-Mod-Template/simplified/"
```

The `id` is the other project's identity, copied from its page or manifest. `name` is for people;
if Tallow is renamed tomorrow, this still points at it. `url` tells a client where to discover it.

## Five kinds, kept apart

| List | Promise | A client should |
|---|---|---|
| `[[requires]]` | Does not work without it | Install it first, or refuse |
| `[[recommends]]` | Works better with it | Offer it |
| `[[conflicts]]` | Breaks with it | Refuse to install both, or warn |
| `[[compatible]]` | Tested together, works | Nothing; it is information |
| `[[replaces]]` | This project supersedes that one | Offer to swap |

Anything not listed is untested, and the page says so. That is different from compatible, and it is
different from conflicting; collapsing the three into "requirements" is how mod pages end up lying.

## Entries without an id

Plenty of what mods depend on is not a DreamWeave project: Tamriel Rebuilt, a Nexus-only mod, a tool.
Name it anyway:

```toml
[[recommends]]
name = "Tamriel Rebuilt"
url = "https://www.tamriel-rebuilt.org/"
reason = "Install the Tamriel Rebuilt component to light the mainland too."
```

People see it; clients cannot resolve it, and the page marks it "not on the network". A `version`
constraint needs an `id`, because checking the version of something you cannot identify is theater.

For content files, use OpenMW's own terms instead: `[openmw] requires_content = ["Tribunal.esm"]` is
a requirement a client can check against the player's load order, and a component can require its
own, like `TR_Mainland.esm` for a Tamriel Rebuilt patch.

## Capabilities

Sometimes you need *a* music framework, not a specific one. A project can `provide` a capability:

```toml
provides = ["dreamweave:music-playlists"]
```

and another can require it:

```toml
[[requires]]
capability = "dreamweave:music-playlists"
name = "A playlist framework"
```

Capabilities are plain strings. Namespace them (`yourname:thing`) so two unrelated projects do not
mean different things by `music`.

## Constraints

A constraint is `*` or comma-separated comparators that must all hold:

| Constraint | Allows |
|---|---|
| `*` | anything |
| `>=1.0` | 1.0 and newer |
| `>=0.49, <0.51` | 0.49 up to, not including, 0.51 |
| `=1.2.0` | exactly 1.2.0 (and 1.2, which has the same precedence) |
| `!=1.1.0` | anything but the broken one |

The operators are `=`, `!=`, `>`, `>=`, `<` and `<=`. There is no `^`, `~` or `||`: each of those
means something slightly different in every ecosystem that has one, and "requires version 2+" is how
nobody knows what you meant. A constraint on another project is evaluated with that project's
versioning scheme, which its manifest states, so `>=0.9` on a decimal project allows 0.963.

## Runtimes

The engine is not a dependency; it is a runtime:

```toml
[runtimes]
openmw = ">=0.49"

[openmw]
lua_api = ">=60"
```

A project runs on any runtime it lists. OpenMW's Lua API revision is separate from its version,
because a development build can have a newer API than the last release.
