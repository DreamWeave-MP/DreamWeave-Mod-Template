"""DreamWeave version and version-constraint grammar.

A version is dot-separated release numbers with an optional SemVer-style pre-release and
build suffix: `1`, `0.51`, `1.2.0`, `2.0.0-beta.3`, `1.4.0+el9`. Release numbers compare
numerically and missing trailing numbers count as zero, so `1.2` and `1.2.0` have equal
precedence. Pre-release and build rules are SemVer 2.0.0 §9-11.

`0.9` is lower than `0.82`, because 9 < 82. Versions are not decimals.

A constraint is `*` or comma-separated comparators that must all hold: `>=0.49, <0.51`.
Operators are `=`, `!=`, `>`, `>=`, `<` and `<=`. There is no `^`, `~` or `||`.
"""

import re
from dataclasses import dataclass
from functools import total_ordering

RELEASE_NUMBER = r"(?:0|[1-9][0-9]*)"
IDENTIFIER = r"[0-9A-Za-z-]+"
VERSION_PATTERN = re.compile(
    rf"^(?P<release>{RELEASE_NUMBER}(?:\.{RELEASE_NUMBER}){{0,5}})"
    rf"(?:-(?P<prerelease>{IDENTIFIER}(?:\.{IDENTIFIER})*))?"
    rf"(?:\+(?P<build>{IDENTIFIER}(?:\.{IDENTIFIER})*))?$"
)
COMPARATOR_PATTERN = re.compile(r"^(?P<operator>>=|<=|!=|=|>|<)\s*(?P<version>\S+)$")
OPERATORS = ("=", "!=", ">", ">=", "<", "<=")


class VersionError(ValueError):
    pass


@total_ordering
@dataclass(frozen=True)
class Version:
    text: str
    release: tuple[int, ...]
    prerelease: tuple[int | str, ...]

    @classmethod
    def parse(cls, text: str) -> "Version":
        if not isinstance(text, str):
            raise VersionError(f"version must be a string, got {type(text).__name__} {text!r}")

        match = VERSION_PATTERN.match(text)
        if not match:
            raise VersionError(
                f"{text!r} is not a DreamWeave version: use numbers separated by dots, "
                "optionally followed by -prerelease or +build (for example 1.2.0 or 2.0.0-beta.1)"
            )

        prerelease_text = match.group("prerelease")
        prerelease: tuple[int | str, ...] = ()
        if prerelease_text:
            identifiers = []
            for identifier in prerelease_text.split("."):
                if identifier.isdigit():
                    if len(identifier) > 1 and identifier.startswith("0"):
                        raise VersionError(
                            f"{text!r}: numeric pre-release identifier {identifier!r} has a leading zero"
                        )
                    identifiers.append(int(identifier))
                else:
                    identifiers.append(identifier)
            prerelease = tuple(identifiers)

        release = tuple(int(number) for number in match.group("release").split("."))
        return cls(text=text, release=release, prerelease=prerelease)

    def precedence_key(self) -> tuple:
        release = self.release + (0,) * (6 - len(self.release))
        if not self.prerelease:
            return (release, 1, ())

        identifiers = tuple(
            (0, identifier, "") if isinstance(identifier, int) else (1, 0, identifier)
            for identifier in self.prerelease
        )
        return (release, 0, identifiers)

    @property
    def is_prerelease(self) -> bool:
        return bool(self.prerelease)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.precedence_key() == other.precedence_key()

    def __lt__(self, other: "Version") -> bool:
        return self.precedence_key() < other.precedence_key()

    def __hash__(self) -> int:
        return hash(self.precedence_key())

    def __str__(self) -> str:
        return self.text

    def next_development(self, build_number: int) -> "Version":
        """The development build that sorts after this version and before its successor.

        1.2.0 -> 1.2.1-dev.N, and 2.0.0-beta.1 -> 2.0.0-beta.1.dev.N.
        """
        release_text = ".".join(str(number) for number in self.release)
        if self.prerelease:
            prerelease_text = ".".join(str(identifier) for identifier in self.prerelease)
            return Version.parse(f"{release_text}-{prerelease_text}.dev.{build_number}")

        bumped = self.release[:-1] + (self.release[-1] + 1,)
        return Version.parse(".".join(str(number) for number in bumped) + f"-dev.{build_number}")


@dataclass(frozen=True)
class Comparator:
    operator: str
    version: Version

    def allows(self, version: Version) -> bool:
        match self.operator:
            case "=":
                return version == self.version
            case "!=":
                return version != self.version
            case ">":
                return version > self.version
            case ">=":
                return version >= self.version
            case "<":
                return version < self.version
            case "<=":
                return version <= self.version
        raise AssertionError(self.operator)

    def __str__(self) -> str:
        return f"{self.operator}{self.version}"


@dataclass(frozen=True)
class Constraint:
    text: str
    comparators: tuple[Comparator, ...]

    @classmethod
    def parse(cls, text: str) -> "Constraint":
        if not isinstance(text, str):
            raise VersionError(f"version constraint must be a string, got {type(text).__name__} {text!r}")

        stripped = text.strip()
        if stripped == "*":
            return cls(text="*", comparators=())
        if not stripped:
            raise VersionError("version constraint is empty; use * to allow any version")

        comparators = []
        for part in stripped.split(","):
            part = part.strip()
            match = COMPARATOR_PATTERN.match(part)
            if not match:
                hint = ""
                if VERSION_PATTERN.match(part):
                    hint = f" (write ={part} for exactly that version, or >={part} for it and newer)"
                elif part.startswith(("^", "~")):
                    hint = " (^ and ~ are not supported; write the range out, e.g. >=1.2, <2)"
                elif "||" in part:
                    hint = " (|| is not supported; constraints are AND-only)"
                raise VersionError(f"{text!r}: {part!r} is not a comparator{hint}")
            comparators.append(Comparator(match.group("operator"), Version.parse(match.group("version"))))

        normalized = ", ".join(str(comparator) for comparator in comparators)
        return cls(text=normalized, comparators=tuple(comparators))

    def allows(self, version: Version) -> bool:
        return all(comparator.allows(version) for comparator in self.comparators)

    def __str__(self) -> str:
        return self.text
