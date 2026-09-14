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
  Meta, Season, Circuit, Constructor, Race, SeasonFile, Outline, Profile,
} from './types';
import { inScope } from './scope';

declare const __DATA_DIR__: string;
const cache = new Map<string, unknown>();

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
export const outline = (circuitId: string): Outline | null => outlines()[circuitId] ?? null;
export const profile = (circuitId: string): Profile | null => profiles()[circuitId] ?? null;

export const circuit = (id: string) => circuits().find((c) => c.id === id) ?? null;
export const constructorById = (id: string) => constructors().find((c) => c.id === id) ?? null;

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

/** Circuits on a season's calendar, in calendar order. */
export function seasonCircuits(year: number): Circuit[] {
  const ids = new Set(races().filter((r) => r.year === year).map((r) => r.circuitId));
  return circuits().filter((c) => ids.has(c.id));
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
