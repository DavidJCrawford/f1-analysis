/** Point at a given fraction of the way round a closed polyline.
 *  The profile records corner positions as distance along the lap; the outline
 *  is the same trace, so arc-length fraction maps between them directly. */
export function pointAtFraction(
  points: readonly (readonly [number, number])[],
  f: number,
): [number, number] {
  const n = points.length;
  const seg: number[] = [];
  let total = 0;
  for (let i = 0; i < n; i++) {
    const a = points[i]!, b = points[(i + 1) % n]!;
    const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
    seg.push(d); total += d;
  }
  let target = ((f % 1) + 1) % 1 * total;
  for (let i = 0; i < n; i++) {
    if (target <= seg[i]!) {
      const a = points[i]!, b = points[(i + 1) % n]!;
      const t = seg[i] ? target / seg[i]! : 0;
      return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
    }
    target -= seg[i]!;
  }
  return [points[0]![0], points[0]![1]];
}
