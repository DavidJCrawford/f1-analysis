const MONTHS = ['January','February','March','April','May','June',
                'July','August','September','October','November','December'];

/** Dates are rendered from the stored string, never parsed through a local
 *  timezone — that is how a schedule becomes subtly wrong. */
export function longDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  if (!y || !m || !d) return iso;
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

export const shortDate = (iso: string): string => {
  const [y, m, d] = iso.split('-').map(Number);
  return y && m && d ? `${d} ${MONTHS[m - 1]!.slice(0, 3)} ${y}` : iso;
};

export const km = (v: number | null): string => (v == null ? '—' : `${v.toFixed(3)} km`);
export const int = (v: number | null): string => (v == null ? '—' : v.toLocaleString('en-GB'));
export const pts = (v: number | null): string =>
  v == null ? '—' : Number.isInteger(v) ? String(v) : v.toFixed(1);

/** An em dash, not a zero. A missing value is not the number nought. */
export const dash = <T>(v: T | null | undefined, f: (x: T) => string): string =>
  v == null ? '—' : f(v);
