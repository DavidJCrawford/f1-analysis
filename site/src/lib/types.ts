export type Tier = 'archival' | 'timing' | 'telemetry' | 'modern';

export interface Meta {
  spineRelease: string;
  source: string;
  counts: Record<'seasons' | 'races' | 'circuits' | 'constructors' | 'drivers' | 'results', number>;
  tiers: Record<Tier, number>;
  dataAsOf: string;
  scheduledThrough: string;
}

export interface Season {
  year: number; races: number; tier: Tier;
  championDriver: string | null; championDriverId: string | null;
  championConstructor: string | null; championConstructorId: string | null;
}

export interface Circuit {
  id: string; name: string; fullName: string; place: string;
  country: string; countryId: string; type: string; direction: string;
  lat: number | null; lon: number | null;
  length: number | null; turns: number | null; racesHeld: number | null;
}

export interface Constructor {
  id: string; name: string; fullName: string; country: string;
  entries: number | null; starts: number | null; wins: number | null;
  podiums: number | null; poles: number | null; titles: number | null;
  points: number | null; bestChampionshipPosition: number | null;
}

export interface Race {
  id: number; year: number; round: number; date: string;
  grandPrixId: string; name: string; shortName: string; officialName: string;
  circuitId: string; circuitLayoutId: string;
  courseLength: number | null; turns: number | null;
  laps: number | null; distance: number | null; tier: Tier;
}

export interface Result {
  pos: string; posNum: number | null; no: string;
  driverId: string; driver: string;
  constructorId: string; constructor: string;
  laps: number | null; time: string | null; gap: string | null;
  reasonRetired: string | null; grid: number | null;
  points: number | null; sharedCar: boolean;
}

export interface Standing { pos: string; points: number | null; champion: boolean; }
export interface DriverStanding extends Standing { driverId: string; driver: string; }
export interface ConstructorStanding extends Standing { constructorId: string; constructor: string; }

export interface SeasonFile {
  year: number; tier: Tier; races: Race[];
  driverStandings: DriverStanding[];
  constructorStandings: ConstructorStanding[];
  results: Record<string, Result[]>;
}

/** Normalised circuit outline, fitted to a unit box, y already flipped for SVG. */
export interface Outline {
  points: [number, number][]; aspect: number;
  declaredLength: number | null; openedYear: number | null;
  sourceId: string; source: string;
}
