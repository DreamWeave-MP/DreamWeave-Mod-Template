+++
title = "Provenance"
description = "What hashes and signatures prove, what they do not, and how keys are meant to work."
weight = 80

[extra]
kind = "guide"
+++

Two different questions get lumped together as "is this safe":

- **Integrity:** are these the bytes the publisher meant? Hashes and signatures answer that.
- **Trust:** should I run what this publisher made? Nothing in a manifest answers that.

A valid signature proves that whoever controls a key, or a CI workflow, produced an artifact. It
does not prove the artifact is harmless, that the author is who they claim, or that the mod does
what its page says. Anyone can sign malware perfectly. Trust is a decision each client and each
player makes, and the protocol refuses to pretend otherwise.

## What every release has

**A SHA-256 and a size for every artifact**, recorded in `mod.lock` in a reviewed commit before the
release exists, and reproduced by CI before publication. A client that checks them knows it has the
publisher's bytes, whichever mirror served them.

**The source revision**, the commit the release's tag points at, when the repository is public.
Anyone can check out that commit and rebuild the archive: same commit, same bytes.

## Sigstore signatures

```toml
[provenance]
sigstore = true
```

CI then signs each archive with [Sigstore](https://www.sigstore.dev/)'s keyless signing, the same
mechanism StroggForge uses for DreamWeave's Rust binaries. There is no key to manage or leak: the
signature is tied to the GitHub Actions workflow that ran, recorded in Sigstore's public
transparency log, and uploaded next to the archive as `<file>.sigstore.json`. The manifest lists it
with the identity to expect:

```json
{
  "format": "sigstore-bundle",
  "url": "https://github.com/OWNER/REPO/releases/download/my_mod-1.0.0/my_mod.zip.sigstore.json",
  "issuer": "https://token.actions.githubusercontent.com",
  "identity": "https://github.com/OWNER/REPO/.github/workflows/build_site.yml@refs/tags/my_mod-1.0.0"
}
```

Verify one yourself:

```sh
cosign verify-blob my_mod.zip \
  --bundle my_mod.zip.sigstore.json \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity https://github.com/OWNER/REPO/.github/workflows/build_site.yml@refs/tags/my_mod-1.0.0
```

That proves the archive was built by that workflow, in that repository, for that tag. It ties the
signature to a GitHub repository, which is provenance, not identity: the project id does not change
if the repository does. Signing publishes the repository and workflow in a public log, so leave it
off for anything you would rather keep out of one.

## Publisher keys

A long-lived publisher key (sign the manifest, carry the key across hosts) is the next step, and it
is deliberately not in this version. The design it has to satisfy:

- **Keys are not identities.** A project's id outlives any key. Losing a key must not orphan a mod.
- **Rotation is continuity.** A new key is introduced by a statement signed with the old one, so a
  client that trusted the old key can follow the chain.
- **Revocation is a statement,** published by the project and signed by a key it trusts, not a
  certificate authority's decision.
- **Clients decide.** Trust on first use, a pinned key, an index's endorsement, or nothing at all
  are all legitimate policies, and choosing one is the client's job.

There is no DreamWeave certificate authority, now or later. A central trust root would be the
central registry this whole design exists to avoid. When publisher keys arrive they will be an
extension first ([Extensions and evolution](@/guide/protocol/evolution.md)), so today's clients
ignore them safely.
