/**
 * Build-time data access.
 *
 * Reads the emitted JSON from site/data/ with node:fs rather than importing it,
 * so nothing is bundled into the client and a 1,172-race corpus never becomes a
 * module graph. Every read is memoised for the life of the build.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type {
  Meta, Season, Circuit, Constructor, Driver, Race, SeasonFile, Outline, Profile,
} from './types';
import { inScope } from './scope';

declare const __DATA_DIR__: string;
const cache = new Map<string, unknown>();

/** Optional read — returns null when the file is absent rather than throwing. */
function loadMaybe<T>(rel: string): T | null {
  try { return load<T>(rel); } catch { return null; }
}

function load<T>(rel: string): T {
  const hit = cache.get(rel);
  if (hit !== undefined) return hit as T;
  const parsed = JSON.parse(readFileSync(join(__DATA_DIR__, rel), 'utf-8')) as T;
  cache.set(rel, parsed);
  return parsed;
}

export const meta = () => load<Meta>('meta.json');

/** Everything below is filtered to the configured scope — see scope.ts. One
 *  switch narrows the routes, the indexes, the entity lists and the counts. */
export const seasons = () => load<Season[]>('seasons.json').filter((s) => inScope(s.year));
export const races = () => load<Race[]>('races.json').filter((r) => inScope(r.year));

export function circuits(): Circuit[] {
  const used = new Set(races().map((r) => r.circuitId));
  return load<Circuit[]>('circuits.json').filter((c) => used.has(c.id));
}

export function constructors(): Constructor[] {
  const entered = new Set<string>();
  for (const s of seasons())
    for (const c of season(s.year).constructorStandings) entered.add(c.constructorId);
  return load<Constructor[]>('constructors.json').filter((c) => entered.has(c.id));
}

/** Counts for what this site actually covers, not for all of F1 history. */
export function counts() {
  const r = races();
  return {
    seasons: seasons().length, races: r.length, circuits: circuits().length,
    constructors: constructors().length,
    results: seasons().reduce((n, s) =>
      n + Object.values(season(s.year).results).reduce((m, v) => m + v.length, 0), 0),
    held: r.filter((x) => x.date <= meta().dataAsOf).length,
  };
}
export const outlines = () => load<Record<string, Outline>>('outlines.json');
export const profiles = () => load<Record<string, Profile>>('profiles.json');

export const season = (year: number) => load<SeasonFile>(`seasons/${year}.json`);

/** Replay manifest for a race, when one has been built. */
export const replay = (year: number, round: number) =>
  loadMaybe<Record<string, unknown>>(`replays/${year}-${round}.json`);
export const outline = (circuitId: string): Outline | null => outlines()[circuitId] ?? null;
export const profile = (circuitId: string): Profile | null => profiles()[circuitId] ?? null;

export const circuit = (id: string) => circuits().find((c) => c.id === id) ?? null;
export const constructorById = (id: string) => constructors().find((c) => c.id === id) ?? null;

/** Drivers who actually took part in a season in scope, in championship order,
 *  with the team they drove for. A driver who changed team mid-season is listed
 *  under the one they raced for most. */
type SeasonDriver = Driver & { constructorId: string; constructor: string };
let driverCache: SeasonDriver[] | null = null;

export function drivers(): SeasonDriver[] {
  if (driverCache) return driverCache;
  const all = load<Driver[]>('drivers.json');
  const byId = new Map(all.map((d) => [d.id, d]));
  const teams = new Map<string, Map<string, { n: number; name: string }>>();
  const order: string[] = [];
  for (const s of seasons()) {
    const f = season(s.year);
    for (const rows of Object.values(f.results))
      for (const r of rows) {
        if (!byId.has(r.driverId)) continue;
        const seen = teams.get(r.driverId) ?? new Map();
        const cur = seen.get(r.constructorId) ?? { n: 0, name: r.constructor };
        seen.set(r.constructorId, { n: cur.n + 1, name: r.constructor });
        teams.set(r.driverId, seen);
      }
    for (const st of f.driverStandings) if (teams.has(st.driverId)) order.push(st.driverId);
  }
  const out: SeasonDriver[] = [];
  for (const id of [...new Set([...order, ...teams.keys()])]) {
    const d = byId.get(id);
    const seen = teams.get(id);
    if (!d || !seen) continue;
    const [constructorId, best] = [...seen].sort((a, b) => b[1].n - a[1].n)[0]!;
    out.push({ ...d, constructorId, constructor: best.name });
  }
  driverCache = out;
  return out;
}

/** Whether a driver has a page — everyone who has started a race in scope does.
 *  Guards the links in result tables, which can name a driver we do not cover. */
export const hasDriverPage = (id: string): boolean =>
  (driverIds ??= new Set(drivers().map((d) => d.id))).has(id);
let driverIds: Set<string> | null = null;

export const driverById = (id: string) => drivers().find((d) => d.id === id) ?? null;

/** A constructor's drivers this season, in championship order. */
export const constructorDrivers = (id: string) =>
  drivers().filter((d) => d.constructorId === id);

/** A constructor's mark as [width, height], or null where there is none —
 *  only the current grid is published. See pipeline/marks.py. */
export const markShape = (id: string): [number, number] | null =>
  ((marks ??= loadMaybe<Record<string, [number, number]>>('marks.json') ?? {}))[id] ?? null;
let marks: Record<string, [number, number]> | null = null;

/** Where the grid lines up, as a fraction of the lap from the finish line.
 *  Measured from a race's own grid, so only circuits that have held one this
 *  season have it — see pipeline/replay.py. */
export const startLine = (circuitId: string): number | null =>
  (loadMaybe<Record<string, { frac: number }>>('startlines.json') ?? {})[circuitId]?.frac ?? null;

/** The team's own colour, from the timing feed — see pipeline/colours.py. */
export const teamColour = (id: string): string | null =>
  (loadMaybe<Record<string, string>>('colours.json') ?? {})[id] ?? null;

/** Where a driver finished each season in scope. */
export function driverSeasons(id: string) {
  const out: { year: number; pos: string; points: number | null; champion: boolean }[] = [];
  for (const s of seasons()) {
    const row = season(s.year).driverStandings.find((d) => d.driverId === id);
    if (row) out.push({ year: s.year, pos: row.pos, points: row.points, champion: row.champion });
  }
  return out.sort((a, b) => b.year - a.year);
}

/** Every race a driver started in scope, newest first, with where they finished. */
export function driverResults(id: string) {
  const out = [];
  for (const s of seasons()) {
    const f = season(s.year);
    for (const r of f.races) {
      const row = (f.results[String(r.round)] ?? []).find((x) => x.driverId === id);
      if (row) out.push({ race: r, result: row });
    }
  }
  return out.sort((a, b) => b.race.year - a.race.year || b.race.round - a.race.round);
}

/** Races held at a circuit, newest first. */
export const racesAtCircuit = (circuitId: string) =>
  races().filter((r) => r.circuitId === circuitId).sort((a, b) => b.year - a.year || b.round - a.round);

/** Seasons a constructor entered, with its finishing position that year. */
export function constructorSeasons(id: string) {
  const out: { year: number; pos: string; points: number | null; champion: boolean }[] = [];
  for (const s of seasons()) {
    const row = season(s.year).constructorStandings.find((c) => c.constructorId === id);
    if (row) out.push({ year: s.year, pos: row.pos, points: row.points, champion: row.champion });
  }
  return out.sort((a, b) => b.year - a.year);
}

/** The latest season in the corpus — the peer group a circuit is measured against. */
export const currentSeasonYear = (): number =>
  Math.max(...seasons().map((s) => s.year));

/** Circuits on a season's calendar, in calendar order — which took a round
 *  number to get right: filtering the circuit list by a set of ids returns them
 *  in whatever order that list happens to be in, which is alphabetical. */
export function seasonCircuits(year: number): Circuit[] {
  const byId = new Map(circuits().map((c) => [c.id, c]));
  const out: Circuit[] = [];
  const seen = new Set<string>();
  for (const r of races().filter((x) => x.year === year).sort((a, b) => a.round - b.round)) {
    const c = byId.get(r.circuitId);
    if (c && !seen.has(c.id)) { seen.add(c.id); out.push(c); }
  }
  return out;
}

export const TIER_LABEL: Record<string, string> = {
  archival: 'Archival', timing: 'Timing', telemetry: 'Telemetry', modern: 'Modern',
};

/** What a tier can and cannot show. Absence is designed, never an empty chart. */
export const TIER_NOTE: Record<string, string> = {
  archival: 'Results and championship record only. Lap-by-lap timing does not exist for this era.',
  timing: 'Lap times and positions are available. Car telemetry does not begin until 2018.',
  telemetry: 'Car and position telemetry available at roughly 240 ms.',
  modern: 'Full timing and telemetry coverage.',
};
