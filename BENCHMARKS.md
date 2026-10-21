# Mod template benchmarks

`bench/bench.jsl` times the package through what it exports: versions parsed and ordered, a git
index read and listed, archives assembled in memory and streamed from disk, a built site checked
and crawled for offline documentation, a repository loaded and described, and the whole build of
one. Everything it reads is generated below the scratch folder from fixed seeds, so two runs time
the same work. Each workload is warmed up, sized to a batch of about a tenth of a second, and
reported as the median of seven batches, with a full collection between them. What a workload
returned is described outside its time (a digest of what it made, the archive read back entry by
entry, the tree a crawl or a build wrote), must be the same for its first, second and last call,
and is printed on a `#` line, so two runs can be told to have done the same work.

```sh
jess run --package jpk/dreamweave-mod-template --package-path jpk \
  --capability filesystem.read --capability filesystem.write \
  jpk/dreamweave-mod-template/bench/bench.jsl <scratch folder> [filter]
```

A filter names a group (`version`, `git index`, `archive`, `site check`, `offline`, `util`,
`model`, `records`, `build`) or a workload with its group in front (`offline: crawl`).

## The move onto l3i 2.0, base against head

- Machine: Intel Core i7-10870H @ 2.20 GHz, 16 threads, shared with other work while this ran.
- Date: 2026-10-13.
- Binary: the verified release build of Jess 0.1.0 on l3i 2.0.2 (Luau 0.742), the same one for
  both sides.
- Base: `e8d316c`, the package as it was imported, with the one fix l3i 2.0 forced (`@dream/vfs`
  became the `@vfs` package), the suite and this bench. Head: `3f9f4b4`, the head as reviewed:
  the last change for speed, `1746cc6`, and the four fixes the review made after it, which put
  back what the faster code had changed for a crawler method replaced on the class, a rewriter
  that answers with what is not text, an archive of what is no plain list, and a list the sort
  refuses part way. Only the last two touch a timed path, a check or two for each entry. The
  bench and the suite's support module are head's on both sides.
- Protocol: the whole bench against base, then head, three times over, back to back under one
  lock; each cell is the median of its three runs. A difference under 5 percent is called no
  change. All 16 digests were the same on both sides in every round.

| Workload | Base, ms | Head, ms | Base / head |
|---|---:|---:|---:|
| version: parse 4,096 release strings | 6.055 | 3.084 | 1.96x |
| version: sort 2,048 numeric and 2,048 decimal versions | 17.782 | 9.448 | 1.88x |
| version: the next development version of 2,048 | 7.480 | 4.777 | 1.57x |
| git index: read 4,096 entries | 3.308 | 1.458 | 2.27x |
| git index: list one project of 16, 256 files on disk | 4.463 | 1.939 | 2.30x |
| archive: 2,048 entries held in memory, as bytes | 9.048 | 4.381 | 2.07x |
| archive: 2,048 entries held in memory, written | 22.729 | 17.221 | 1.32x |
| archive: 193 files streamed from disk, written | 46.078 | 45.987 | no change |
| site check: 46 pages of a built site | 129.536 | 31.189 | 4.15x |
| offline: rewrite 46 pages held in memory | 267.039 | 95.081 | 2.81x |
| offline: crawl a project of 33 pages into a folder | 249.864 | 52.445 | 4.76x |
| util: walk the 85 files of a built site | 1.012 | 0.931 | 1.09x |
| model: load a repository of 24 projects | 16.267 | 13.090 | 1.24x |
| records: the release document, manifest and index entry of 24 projects | 8.265 | 8.012 | no change |
| build: list the archive entries of 24 projects | 27.688 | 12.768 | 2.17x |
| build: a repository of 24 projects, site and archives | 450.898 | 327.799 | 1.38x |

The same A/B was run twice more. With glibc's trim and mmap thresholds raised on both sides
(`MALLOC_TRIM_THRESHOLD_` and `MALLOC_MMAP_THRESHOLD_` at 1 GiB) no ratio moved by more than 0.07
but the site check's, 4.31x. Before the last of the fixes, on a busier machine, every time was 3
to 10 percent higher and every ratio within a tenth of the one here; the furthest was the archive
as bytes, 1.87x with 5.4 ms at head. That row builds a 2.7 MB string a call and its head time
goes with what the process did before it: 4.0 ms when the archive group runs alone (2.27x), 4.4
to 5.4 ms in the whole bench.

None of this came from the dialect's syntax. The package is text and files, with no table of
numbers for the data plane to take, and the comprehensions, the `any` reducers, the slice and the
record patterns it now has sit in code that runs a few times a build: each change that carried
them was measured against the commit before it and moved nothing. What moved is the work the
old code did per byte, per tag and per file. The site check read every tag one character at a
time, each character a string of its own matched against a pattern, and asked the disk about
every link; it now reads a page where it stands, by byte, and judges each distinct link once.
The crawler ran four patterns over every tag and three over every page, and resolved every
reference against the disk every time it saw it; it now finds the few attributes and URLs that
matter by plain search, remembers what a page's references came to, and keeps the files a crawl
has looked for. A crawl also wrote each page it staged through `jess.fs.write`, which puts a
temporary beside the file and waits for the disk before renaming it, 0.9 ms a file on this
machine; staged pages now go straight to their files, as staged assets always did. Archive
records are written into one buffer each in place of a dozen or more short strings joined, a
version strips zeros only where there are zeros, and a path is normalized only where it is not
normal already.

Two rows did not move and will not from here. An archive streamed from disk is the SHA-256 and
the CRC of its bytes and the reads and writes of them. The records are a few tables built per
project and then `@dreamweave/site/json`'s encoder, which is that package's. Of the whole build,
about 145 ms of the 328 left is the site generator's own build of the offline site (nine builds
of the bench's repository on their own: median 143.7 ms, 136 to 152), and that package writes
every page through the same `jess.fs.write`.

### Each change for speed, against the commit before it

Measured the same way (three rounds, alternating, one lock for each change), over the rows the
change feeds. Three of them are small: `76702fc` on the crawl, `d1efe82` on the load and
`d3603f5` on the walk sit between 6 and 8 percent, just clear of what is called no change.

| Commit | Change | Row | Before, ms | After, ms | |
|---|---|---|---:|---:|---:|
| `06fc1fa` | normalize a path only where it needs it | git index: read | 3.290 | 1.473 | 2.23x |
| | | git index: list one project | 4.435 | 2.625 | 1.69x |
| `6052b03` | split a version with `string.split`, strip zeros and metadata only where present | version: parse | 6.048 | 3.038 | 1.99x |
| | | version: sort | 17.794 | 11.423 | 1.56x |
| | | version: next development | 7.560 | 4.873 | 1.55x |
| `c234fcc` | keep only a folder's entries as the index is read, sort relative paths as strings | git index: list one project | 2.637 | 1.953 | 1.35x |
| `117bffb` | one buffer per zip record | archive: as bytes | 8.711 | 4.886 | 1.78x |
| | | archive: written | 23.565 | 19.459 | 1.21x |
| `9703c7e` | sort an archive's paths as plain strings | archive: as bytes | 4.889 | 3.981 | 1.23x |
| `6e9e0de` | hand small pieces to the file and the digest in batches | archive: written | 18.834 | 16.465 | 1.14x |
| `c2ec9a1` | read a page for the check byte by byte | site check | 128.470 | 83.554 | 1.54x |
| `cde8552` | ask the disk about each linked path once a check | site check | 84.181 | 35.690 | 2.36x |
| `40f68c2` | judge each distinct link once | site check | 35.387 | 30.099 | 1.18x |
| `2a4bf8a` | find a tag's attributes by plain search | offline: rewrite | 259.700 | 181.225 | 1.43x |
| | | offline: crawl | 247.508 | 194.868 | 1.27x |
| `76702fc` | look for an escape or an entity before substituting | offline: rewrite | 193.124 | 174.873 | 1.10x |
| | | offline: crawl | 196.571 | 185.319 | 1.06x |
| `17b26cc` | find a stylesheet's URLs by plain search | offline: rewrite | 183.121 | 146.608 | 1.25x |
| | | offline: crawl | 187.790 | 164.595 | 1.14x |
| `4ae016d` | remember a page's references and a crawl's files | offline: rewrite | 151.996 | 95.166 | 1.60x |
| | | offline: crawl | 165.291 | 92.408 | 1.79x |
| `d1efe82` | find a path's last name from its last slash | build: list entries | 14.087 | 13.025 | 1.08x |
| | | model: load | 15.009 | 14.208 | 1.06x |
| `d3603f5` | one look at the disk per walked name | util: walk | 0.995 | 0.923 | 1.08x |
| | | model: load | 14.506 | 13.330 | 1.09x |
| `3ffec6c` | equal digits are an equal number | version: sort | 11.497 | 9.462 | 1.22x |
| `1746cc6` | write a staged page straight to its file | offline: crawl | 92.303 | 53.220 | 1.73x |
| | | build: a repository | 419.585 | 332.903 | 1.26x |

### What it costs to load

A cold process loads the package's nine modules in 32.7 ms at head against 27.7 ms at base, the
dependencies loaded first and left out (median of eleven cold runs a side, alternating): the
crawler 3.2 ms to 5.7 and the site check 2.9 ms to 4.1, the two modules that grew. Their
dependencies (`@vfs`, `@dreamweave/site`, `@magick` and what those load) take 224 to 230 ms
either way, and move more from run to run than the 5 ms the package gained, so loading everything
is about 257 ms on both sides. One crawl of a small project pays the difference back.

### Tried, measured, and taken out

- One `jess.fs.stat` in place of `isDir` and `isFile` when the crawler resolves a file: no change.
- A crawl-wide memory of where references with a scheme or a rooted path point: 1.03x on the
  crawl, within noise.
- Lower-casing a tag's name in the site check only when it holds an upper-case letter: 1.05x,
  within noise.
- Reading an index entry's big-endian words with one read and a byte swap moved nothing (1.04x)
  and is kept as the plainer spelling, not as a gain.
- String interpolation in place of `..` in the version module's inner functions measured 3 to 6
  percent slower and was put back to concatenation; hot paths concatenate.

## Which modules are native, and why

Jess compiles to machine code only what is marked (`--!native` on a module, `@native` on one
function), and every load pays for what is marked. A module carries `--!native` when a row below
spends its time there and the module is small (12 KB or less); a larger module carries `@native`
on the functions the row spends its time in, and nothing else.

Measured 2026-10-15 with `jess 0.1.0`, the verified release build of jess `07c38cb` on l3i
2.0.3, on the i7-10870H, the one-minute load 1.43 and 1.46 at the start of the two
sessions. In each session the bench ran alternately on this package and on a copy of it with
every module marked, three fresh runs of `bench/bench.jsl` each, every run's row the median of
its batches; a column is the median of the three, and a ratio is against the all-marked runs of
the same session. Which functions a row spends its time in comes from `jess run --profile` of
that row alone, unmarked. The load cost is a fresh `jess run --package <this package>
--package-path jpk` of a script that only requires `@dreamweave/mod-template`, the two sides alternating, the
median of five each after one warm-up.

| Requiring `@dreamweave/mod-template` | All marked | This state |
| --- | ---: | ---: |
| Unmarked | 0.213 s | 0.195 s |
| Final | 0.218 s | 0.203 s |

| Row | All marked (ms) | Unmarked / all marked | Final (ms) | Final / all marked |
| --- | ---: | ---: | ---: | ---: |
| version: parse 4,096 release strings | 2.957 | **1.406×** | 2.942 | 0.995× |
| version: sort 2,048 numeric and 2,048 decimal versions | 9.152 | **2.116×** | 9.145 | 0.999× |
| version: the next development version of 2,048 | 4.774 | **1.311×** | 4.718 | 0.988× |
| git index: read 4,096 entries | 1.493 | **1.440×** | 1.450 | 0.971× |
| git index: list one project of 16, 256 files on disk | 1.974 | **1.358×** | 1.880 | 0.953× |
| archive: 2,048 entries held in memory, as bytes | 4.234 | **1.334×** | 4.233 | 1.000× |
| archive: 2,048 entries held in memory, written | 17.06 | **1.089×** | 16.96 | 0.994× |
| archive: 193 files streamed from disk, written | 45.76 | 0.989× | 45.29 | 0.990× |
| site check: 46 pages of a built site | 29.62 | **2.154×** | 30.81 | 1.040× |
| offline: rewrite 46 pages held in memory | 93.37 | **1.154×** | 99.51 | **1.066×** |
| offline: crawl a project of 33 pages into a folder | 52.30 | **1.211×** | 57.20 | **1.094×** |
| util: walk the 85 files of a built site | 0.8588 | 1.033× | 0.8767 | 1.021× |
| model: load a repository of 24 projects | 12.52 | **1.061×** | 12.21 | 0.975× |
| records: the release document, manifest and index entry of 24 projects | 8.399 | **1.062×** | 8.149 | 0.970× |
| build: list the archive entries of 24 projects | 13.36 | **1.332×** | 12.79 | 0.958× |
| build: a repository of 24 projects, site and archives | 314.8 | 1.035× | 321.3 | 1.020× |

What carries the directive (every module and function here is one a row spends its time in,
unmarked):

- Whole: `archive`, `git_index`, `util`, `version`.
- `build`, by function: `documentationSources`.
- `model`, by function: `frontMatter`, `model.load`.
- `offline`, by function: `escapeAttribute`, `Crawler.sitePath`, `rewriteSrcset`,
  `rewriteAttribute`, `rewriteTag`, a closure at line 557.
- `records`, by function: `listed`.
- `sitecheck`, by function: a closure at line 77, `document`, `normalizePath`.

The two rows above 5% are the offline copy of a site: rewriting 46 pages held in memory (1.07x)
and crawling 33 pages into a folder (1.09x), about 6 ms more on calls of 50 ms to 100 ms that a
build makes once, where this state saves 15 ms on every load of the package. Their remaining
time is spread over the rest of `offline` past the rewriters marked here.
