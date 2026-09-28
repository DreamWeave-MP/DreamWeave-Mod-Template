+++
title = "Versions and releases"
description = "Version grammar, the two ordering schemes, constraints, channels and update checks."
weight = 30

[extra]
kind = "reference"
+++

## Grammar

```text
version     = release [ "-" prerelease ] [ "+" build ]
release     = integer *5( "." number )
integer     = "0" / ( %x31-39 *DIGIT )              ; no leading zeros
number      = integer                                ; numeric scheme
number      = 1*DIGIT                                ; decimal scheme: leading zeros allowed
prerelease  = identifier *( "." identifier )         ; numeric identifiers have no leading zeros
build       = identifier *( "." identifier )
identifier  = 1*( ALPHA / DIGIT / "-" )
```

A release has between one and six numbers.

## Precedence

Precedence compares release numbers first, then pre-release, exactly as
[SemVer 2.0.0 §11](https://semver.org/#spec-item-11) does for pre-releases: a version with a
pre-release is lower than the same release without one, and identifiers compare numerically when
both are numeric, in ASCII order otherwise, numeric before alphanumeric, a longer list winning when
all shared identifiers are equal. Build metadata MUST be ignored.

How release numbers compare depends on the project's `versioning`:

**numeric.** Compare as a list of integers, missing trailing numbers being `0`.
`1.2 = 1.2.0 < 1.2.9 < 1.2.10`, and `0.9 < 0.82`.

**decimal.** Compare the first number as an integer. Compare each later number as the digits after a
decimal point: strip its trailing zeros, then compare the digit strings character by character,
where a string that is a prefix of another sorts first and a missing number is the empty string.
`0.5 = 0.50 < 0.54 < 0.6 < 0.82 < 0.9 < 0.963 < 0.97 < 1.0`, and `0.05 < 0.5`.

Versions of two different projects are never compared with each other. Two releases of one project
MUST NOT have equal precedence.

## Constraints

```text
constraint  = "*" / comparator *( "," comparator )
comparator  = operator version
operator    = "=" / "!=" / ">" / ">=" / "<" / "<="
```

Whitespace around operators and commas is allowed. A version satisfies a constraint when it
satisfies every comparator, by precedence under the target project's scheme; `*` is satisfied by
every version. There is no disjunction, no caret or tilde, and no implicit exclusion of pre-releases:
a client that should not offer pre-releases filters them itself.

Runtime constraints (`runtimes.openmw`, the OpenMW extension's `lua_api`) use the numeric scheme.

## Channels and heads

A release's `channel` is a lowercase token. `stable` is the default. `development` is a rolling
build: its version is derived from the newest tagged release so that it sorts after it and before
any successor (numeric `1.2.0` → `1.2.1-dev.N`; decimal `0.963` → `0.9631-dev.N`), and it is
replaced on every push. Its artifacts and their digests change with it.

A channel's head is its highest-precedence release with `status: available`.

## Checking for an update

Given an installed project `P` at version `I`, a configured channel `C`, and the runtime the client
targets:

1. Fetch `P`'s manifest from the origin the client trusts for `P`. Reject it if `project.id` is not
   `P`.
2. Take `channels[C].version` as the candidate. If there is none, there is no update on `C`.
3. The candidate is an update when it has higher precedence than `I`, or when the installed release
   is listed as `yanked`.
4. Drop it if its `runtimes` do not allow the client's runtime and version, if its `platforms` are
   non-empty and exclude the client's, or if it lists a `critical_extensions` entry the client does
   not implement.
5. Resolve its `requires` relationships and check its `conflicts` against what is installed.

A client that wants "beta or anything newer from stable" takes the higher of the two heads. That is
client policy; the protocol does not rank channels.

Clients MUST NOT use page timestamps, GitHub's "latest release", file names or URLs to decide what
is newest.
