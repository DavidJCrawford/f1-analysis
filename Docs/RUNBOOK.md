# RUNBOOK — F1 Analysis

Operating procedures for a site that is **a weekly publication, not a build**.

- **Companion documents:** [SPEC.md](SPEC.md) §12.2 states the constraint;
  [build-and-release](knowledge/engineering/build-and-release.md) and
  [data-pipeline](knowledge/engineering/data-pipeline.md) explain the mechanism;
  [provenance-and-staleness](knowledge/policies/provenance-and-staleness.md)
  defines the states this runbook puts pages into.
- **Status:** the commands below are the **contract the pipeline must
  implement**. As of 2026-09-14 no application code exists — the project is at
  Phase 0. Treat mismatches between this document and the code as defects in
  whichever was written second, and fix both.

---

> **What is built, and what is planned.** This runbook was written against a
> per-round, two-pass ingest (`make fetch YEAR= ROUND=`, `make refresh`,
> provisional-then-final) that does not exist. The pipeline that does exist is
> simpler: whole-season targets that cache every response and are safe to
> re-run, listed by `make help` and used in §2 and §9. FastF1 is not used
> either — the race data comes from OpenF1 directly.
>
> Sections 3–8 keep the *judgement* they were written for — calendar traps,
> absence handling, amendments, what to re-check — and their command blocks
> have been corrected to real targets. Where a concept has no implementation
> (`make doctor`, `source_sha256`, provisional/final passes), it is marked
> **not built** rather than quietly left as if it worked.

## 0. Why there is a human in this loop at all

Three facts, none of which is negotiable:

1. **GitHub-hosted runners cannot fetch F1 data.** The live-timing archive
   blocks datacenter IP ranges, including Actions runners. Cloud cron runs
   return empty data — not errors, *empty data*. FastF1's own mirror fallback
   (`livetiming-mirror.fastf1.dev`) is currently dead: 404 for every path.
2. **Stewards amend results for days after a race.** Penalties land after the
   flag. Appeals succeed. Classifications move.
3. **The free jolpica dump runs 14 days behind.**

So: **a human on a residential connection runs the ingest, and CI only ever
builds from committed data.** CI never touches an F1 endpoint.

> If you find yourself editing a workflow file to make CI fetch from
> `livetiming.formula1.com`, stop. It will appear to work — it will return 200s
> with empty bodies — and it will publish empty races.

---

## 1. One-time setup

**The machine matters.** Ingest must run from a residential connection. A VPN
terminating in a datacenter will fail the same way CI does. If you are on a
corporate VPN, drop it before fetching.

```bash
# Toolchain
uv sync --frozen          # Python 3.12, fastf1 3.8.3, pyarrow, pydantic, pandera
npm ci                    # Node 22+, lockfile committed
```

Set the FastF1 cache **outside the repository**, permanently, in your shell
profile:

```bash
export FASTF1_CACHE="$HOME/.cache/f1-analysis"
```

This is the cleanest reproducibility lever — it sits above the OS default in
FastF1's resolution order (explicit `enable_cache()` path → `FASTF1_CACHE` → OS
default). Keeping it outside the repo also keeps it out of `actions/cache`,
whose quota is 10 GB per repository with 7-day eviction; a season of `.ff1pkl`
is a bad tenant there.

**Checklist:**

- [ ] `npm ci` succeeds in `site/`
- [ ] `python3 --version` is 3.10 or later
- [ ] `make spine` downloads an F1DB release and writes `.cache/f1db/.release`
- [ ] `make replays` fetches from OpenF1 and writes `site/public/replays/`
- [ ] `make verify` runs and reports zero start-line and lap-counting problems

*Not built:* `make doctor`, `uv sync` (there is no Python lockfile), and
`FASTF1_CACHE` (FastF1 is not used).

---

## 2. The standard post-race run

This is the procedure for ~90% of weekends. Budget **20–40 minutes**, most of it
unattended.

### When to run it

**Twice.** This is the single most important operational habit.

| Pass | When | Purpose |
| --- | --- | --- |
| **Pass 1 — provisional** | Within a few hours of the flag | Publish the race promptly, in the `provisional` state, with derived metrics suppressed |
| **Pass 2 — final** | After the window closes: **the later of** 72 h post-session **or** the F1DB release for that round landing | Flip to `final`, release derived metrics, catch any amendment |

Both conditions on pass 2, because a release arriving at 36 hours can still
predate a stewards' decision, and a quiet weekend can see a release delayed past
72 hours.

### The run

```bash
# 0. Start clean.
git pull --ff-only origin main

# 1. The season spine — results, standings, entities. Fast, no race data.
make spine          # download the current F1DB release
make emit           # F1DB CSV -> canonical JSON in site/data/

# 2. The race itself. Both read the timing feed and cache every response
#    under .cache/openf1, so a re-run costs nothing and is safe to repeat.
make replays        # positions, running order, laps, pit and retirement spans
make colours        # team colours, if the grid changed

# 3. Score the replays against what is known independently of them.
make verify

# 4. Build, then read what actually changed.
make build
git status --short
git diff --stat
```

**`make verify` is the gate that matters** and is worth reading rather than
glancing at. It scores every replay against three things it cannot have got
from the replay: the starting grid, the classified result, and the lap count.
Numbers that should hold, as of 2026-09-16:

| Check | Expected |
| --- | --- |
| Grids reproduced exactly | 8 of 14, 26 cars out of place in all |
| Closing orders exact | 6 of 14, 17 cars out of place in all |
| Cars not lined up behind the start line | **0** |
| Lap-counting problems | **0** |

The last two are absolutes: anything above zero is a fault, not a tolerance.
The first two drift with the quality of a round's feed — a round getting
*worse* is the signal, not the absolute number.

**The feed backfills, so a cache is not a final answer.** Melbourne's opening
was placeholder when first fetched and is real data now; refetching turned a
replay that opened three minutes late into one that opens on the grid. If a
round looks thin, delete its cached chunks and re-run before concluding the
data does not exist:

```bash
rm -f .cache/openf1/loc_<session_key>_*.json
make replays
```

### Read the diff before you commit

A normal race weekend rebuilds **one race directory out of ~190**. If the diff
shows more, something is wrong and you should understand it before pushing.

| Diff shape | Meaning |
| --- | --- |
| One race directory + season standings + affected team-season pages | **Normal.** Standings recompute downstream. |
| One race directory only, no standings change | Suspicious — did the emit stage run? |
| Many past races changed | Either a pipeline change touched the dependency closure (fine, expected) or an **amendment** landed (check §6) |
| Every race changed | Almost always a serialisation or rounding change. **Do not push.** The build is supposed to be a pure function — rebuilding an unchanged race must produce a byte-identical file. |

```bash
# 5. Commit the data with the build, and push. Pushing main deploys.
git add site/data site/public/replays
git commit -m "ingest: 2026 R17 Singapore"
git push
```

**Pushing `main` deploys.** The GitHub Actions workflow builds and publishes to
Pages; there is no PR gate, so `make verify` before pushing is the gate.

### Post-deploy checklist

- [ ] The race page renders and carries a **provisional** notice (pass 1)
- [ ] The "data as of" stamp shows the right F1DB release and ingest time
- [ ] Derived metrics are **absent** on pass 1, **present** on pass 2
- [ ] Championship standings updated
- [ ] Session times render with a visible timezone label
- [ ] Search finds the new race

---

## 3. Timing and the calendar

### Triple-headers and compressed weekends

Three races in three weekends — or a sprint weekend immediately followed by a
conventional one — breaks the two-pass rhythm, because pass 2 for race *N*
collides with pass 1 for race *N+1*.

**The rule: never skip pass 2. Batch it instead.**

```bash
# There is no per-round target. Both of these do the whole season and skip
# anything already cached, so running after each race costs one race.
make spine emit
make replays
make verify
```

*Not built:* `make refresh`, `source_sha256`, and the provisional/final
two-pass model. The equivalent today is that **the feed backfills**: a round
fetched within hours of the flag may hold less than the same round fetched a
day later. Re-running does not refetch a cached chunk, so to pick up a
correction, delete that session's chunks first — see §2.

**During a triple-header, run the batch after each race** rather than deferring
to the end. A three-race backlog of provisional pages is a much worse state than
three small ingests, because the standings are wrong the whole time.

### Sprint weekends

Sprint weekends have more sessions and a different ordering. The pipeline keys
on **Race-type sessions**, not meetings — this matters:

> **Pre-season tests are meetings but not races.** In 2026 the season index has
> 16 meetings and only 14 sessions named "Race". Any incremental build keyed on
> meetings will double-count the two test meetings.

If a "race" in January or February appears in the calendar, the source has
picked up a test meeting. Do not ingest it as a race.

---

## 4. When the maintainer is away

The honest position: **the site degrades gracefully and nothing breaks.**

If no ingest runs after a race:

- The site stays up. It is static.
- The new race simply does not appear.
- **The previous race stays `provisional` forever**, with derived metrics
  suppressed and a notice on the page. This is the designed failure mode and it
  is truthful — it says results may still change, which remains true.
- Standings are stale but internally consistent. They are never *wrong*, only
  *behind*.

**What must not happen:** someone attempting to "fix" it by making CI fetch.
See §0.

### Before a planned absence

- [ ] Run pass 2 on every outstanding race so nothing sits `provisional`
- [ ] Push and confirm the deploy is green
- [ ] If the absence spans a race: decide whether to accept the gap, or hand
      over (below)

### Handing over

A second person can run the ingest if they have: the repository, `uv sync
--frozen` + `npm ci`, `FASTF1_CACHE` set, a **residential connection**, and
push access. Nothing else is machine-specific — the FastF1 cache rebuilds itself
on first fetch, at the cost of one download.

### The permanent fix, when this becomes a burden

A **self-hosted runner on a residential connection**. It is the same thing,
automated, and it is the documented upgrade path. Before building it, spend an
hour on the open question in
[build-and-release](knowledge/engineering/build-and-release.md): *does the
FastF1 mirror ever serve from a GitHub-hosted runner?* It is 404 from everywhere
tried so far, but a throwaway workflow would settle whether the local-ingest
constraint is permanent. If it ever lifts, this entire runbook collapses to "CI
does it".

---

## 5. Failure playbooks

### Fetch returns empty data, or 403

| Check | Fix |
| --- | --- |
| Are you on a VPN or corporate network? | Disconnect. Datacenter egress is blocked. |
| Is the session actually over? | The archive populates after the session ends. |
| Does the path exist? | Round numbers come from F1DB; re-run `make spine emit`. |
| Is it just the mirror failing? | Expected — the mirror is dead (404 everywhere). The primary should still serve from residential. |

**Never** conclude "the data isn't published yet" without checking your egress
first. That is the single most common misdiagnosis on this project.

### `RateLimitExceededError`

FastF1 enforces a 250 ms floor between all requests, **200 calls/hour for
jolpi.ca** and 500 calls/hour for other APIs. Cached requests do not count.

- Wait. The window is hourly.
- Do not parallelise the fetch stage. The limiter is per-process and you will
  simply trip it faster.
- If you are backfilling, expect to spread it over hours — see §7.

### Everything looks stale after a FastF1 upgrade

Expected. `ignore_version` defaults to `False` because reusing a cache written
by a different FastF1 version is documented as *"not recommended — incompatible
cached data may cause crashes or errors."* A version bump silently invalidates
every `.ff1pkl` you have.

```bash
# Re-fetch the current season only; leave history alone until you need it.
rm -rf .cache/openf1 && make replays        # forces a full refetch
```

Record `fastf1.__version__` alongside the cache so this is diagnosable rather
than mysterious.

### CI published an empty or half-built race

This is the failure mode the pipeline is explicitly designed to make **loud**.
If it happened silently, the stale-manifest gate is broken — fix the gate, not
just the data.

```bash
rm -f .cache/openf1/loc_<session_key>_*.json && make replays
make verify                              # confirm the manifest matches disk
```

### Build exceeds the 10-minute Pages deploy window

The deploy step — not the build — times out at 10 minutes. Order of
investigation:

1. **Did the incremental cache restore?** Grep CI logs for Astro's re-render
   warning. `build.concurrency > 1` disables the cache: the build still
   *succeeds*, it just silently re-renders every page. This is a log-level
   failure, not an exit code.
2. **Did you edit middleware?** Middleware edits do not invalidate the cache.
   Run `astro build --force` once.
3. **Is the `actions/cache` key right?** It must be keyed on the emitted data
   digest so a data change invalidates cleanly and nothing else does.

### Size gate fails (`dist` over ~700 MB)

The published-site ceiling is 1 GB and the gate trips early on purpose.

- Check whether replay payloads were emitted at 5 Hz instead of the 2 Hz
  default. That alone roughly doubles them (1.31 MB vs 623 KB per race).
- If the corpus has genuinely outgrown the cap, execute the split: telemetry
  moves to a separate data repository served via Releases. This is already the
  recommendation in SPEC §17 — the gate firing is the signal to stop deferring
  it.

### three.js upgrade broke the build

Follow the upgrade checklist in
[build-and-release §7](knowledge/engineering/build-and-release.md). The
blocking pin is **`postprocessing`**, which peers `three >= 0.168.0 < 0.187.0`.
The r187 release due around November 2026 will break the build the moment
three.js is bumped. `camera-controls` has no upper bound and does not gate.

Pin three.js **exactly**. `^` ranges are unsafe on `0.x` semver.

---

## 6. Amendments

An amendment is a result that changed *after publication*. Detection is
machine-driven — it is not your job to notice.

**The signal:** a changed `source_sha256`, or a diff in a monitored field —
`positionNumber`, `positionText`, `points`, `reasonRetired`, `gapLaps`,
`timeMillis`.

```bash
make replays && make verify
#  -> detects the diff, sets classification: amended, emits the amendment note
make verify
```

**Three rules, non-negotiable:**

1. **Amendments are additive.** The dated note stays on the page permanently.
   Silent correction is how a reference loses the right to be trusted.
2. **Downstream recomputation is mandatory.** An amended race invalidates season
   standings, affected team-season pages, driver records and any record page the
   result touches. The incremental `cacheKey` includes the race payload hash so
   this happens automatically — verify it did.
3. **Write the note in the site's voice.** Factual, dated, neutral:

   > Amended 2026-09-16. Car 44 reclassified from 4th to 5th following a
   > post-race penalty. Championship standings updated accordingly.

   No apology, no explanation of process, no hedging. See
   [editorial-voice](knowledge/policies/editorial-voice.md).

---

## 7. Backfill and full rebuild

The whole corpus is roughly **180–200 race sessions across 2018–2026** for
telemetry tiers, and ~1,172 races for results tiers. A full telemetry rebuild is
a weekend job; an incremental one is minutes.

```bash
# Backfill a season. Rate limits make this slow by design - let it run.
make spine emit        # every season F1DB carries
make replays           # only rounds in scope; widen scope.ts first
make verify
```

Guidance:

- **Backfill one season per sitting.** Commit between seasons so a failure never
  costs more than one season of work.
- **Expect a large diff.** Review the *shape*, not every file.
- **Do not backfill during a race weekend.** The current season takes priority
  and you do not want the two diffs interleaved.
- A full rebuild that produces diffs on races you did not intend to touch means
  the build is not a pure function. Investigate before committing — canonical
  JSON serialisation and fixed float rounding exist precisely to prevent this.

---

## 8. Periodic maintenance

| Cadence | Task |
| --- | --- |
| Each race weekend | The two-pass ingest (§2) |
| Monthly in season | Confirm no race is stuck `provisional`; check the size gate headroom |
| Quarterly | Review pinned versions; run the three.js upgrade checklist if a bump is wanted |
| Quarterly | Re-check the **gating legal items** (below) |
| Off-season | Backfill a historical season; re-measure performance budgets; revisit open items |
| Pre-season | Confirm the new season's `Index.json` parses; confirm test meetings are excluded |

### Gating legal items — review until resolved

These are from [SPEC §13](SPEC.md) and
[data-licensing](knowledge/policies/data-licensing.md). They are **not** closed:

- [ ] **F1DB provenance.** Its CC BY 4.0 is a claim by a compiler about data he
      did not create, and its README documents no upstream sources. Ask the
      maintainer directly before it becomes load-bearing.
- [ ] **MultiViewer terms.** No terms of use are published. Their geometry is
      **blocked** until contact is made.
- [ ] **F1 fan-site disclaimer wording.** The exact current wording is
      unverified — both candidate URLs 404. Confirm before launch.
- [ ] **Never link `ergast.com`.** It shut down after 2024 and the domain now
      serves gambling spam. Attribution names it in plain text only.

### Correctness traps to re-assert in review

Two rules that produce *confidently wrong* pages rather than obviously broken
ones, and so will never announce themselves:

- **Retirement causes and laps-down margins for 2024–2026 must come from F1DB,
  not jolpica.** jolpica collapses causes from **2024** onward — not 2025 as its
  own docs state.
- **Session times are stored as UTC with an explicit circuit timezone and always
  rendered with a visible label.** A rendered time without a timezone is a
  defect.

---

## 9. Quick reference

```bash
make help              # every target, with what it does
make spine emit        # season results and entities, from the F1DB release
make replays           # race positions from the timing feed (cached; slow first time)
make colours           # team colours, joined from the feed by car number
make verify            # score the replays against grid, result and lap count
make outlines profile  # circuit geometry and corner detection
make build             # the site and its search index
make check             # type check
make preview           # serve what was built
```

### What `make verify` actually checks

Not a test suite — three scores against facts the replay cannot have produced
itself. The starting grid, the classified result, and the lap count. Cars out
of place against the **start line** and **lap-counting problems** must both be
zero; the grid and closing-order scores drift with feed quality, so watch for a
round getting worse rather than the absolute number.

There is no CI gate. Pushing `main` deploys, so this is the gate.

### If you remember nothing else

1. **`make verify` before you push.** There is nothing else between a bad
   replay and the live site.
2. **The feed backfills.** A round that looked thin months ago may be complete
   now. Delete its cached chunks and re-run before concluding otherwise.
3. **Read the diff before committing.** The emit is a pure function: rebuilding
   unchanged data must produce byte-identical files. Everything changing is a
   serialisation bug, not a data update.
4. **Never draw what is not there.** Every absence on this site is deliberate
   and most of them were once a bug that drew something plausible instead —
   see SPEC §6.6.
