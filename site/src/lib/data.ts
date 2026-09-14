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
export const seasons = () => load<Season[]>('seasons.json');
export const circuits = () => load<Circuit[]>('circuits.json');
export const constructors = () => load<Constructor[]>('constructors.json');
export const races = () => load<Race[]>('races.json');
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
