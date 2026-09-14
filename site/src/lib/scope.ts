/**
 * What the site covers.
 *
 * `null` means all of Formula 1 history — the encyclopaedia SPEC §1 describes,
 * with its four coverage tiers. An array of years narrows everything to those
 * seasons: routes, indexes, entity lists and counts all derive from this, so
 * widening the scope again is a one-line change here plus a rebuild.
 *
 * Currently narrowed to the current season by decision, which supersedes the
 * archival-first roadmap in SPEC §16 — see SPEC §4.3.
 */
export const SEASON_SCOPE: number[] | null = [2026];

export const inScope = (year: number): boolean =>
  SEASON_SCOPE === null || SEASON_SCOPE.includes(year);
