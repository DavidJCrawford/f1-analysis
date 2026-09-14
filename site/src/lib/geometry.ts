export type Vec = readonly [number, number];

function lengths(points: readonly Vec[]): { seg: number[]; total: number } {
  const seg: number[] = [];
  let total = 0;
  for (let i = 0; i < points.length; i++) {
    const a = points[i]!, b = points[(i + 1) % points.length]!;
    const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
    seg.push(d); total += d;
  }
  return { seg, total };
}

/** Point at a given fraction of the way round a closed polyline.
 *  The profile records corner positions as distance along the lap; the outline
 *  is the same trace, so arc-length fraction maps between them directly. */
export function pointAtFraction(points: readonly Vec[], f: number): [number, number] {
  const { seg, total } = lengths(points);
  let target = ((((f % 1) + 1) % 1)) * total;
  for (let i = 0; i < points.length; i++) {
    if (target <= seg[i]!) {
      const a = points[i]!, b = points[(i + 1) % points.length]!;
      const t = seg[i] ? target / seg[i]! : 0;
      return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
    }
    target -= seg[i]!;
  }
  return [points[0]![0], points[0]![1]];
}

/**
 * Point plus the outward-facing unit normal at that fraction.
 *
 * The normal comes from the local tangent, not from a ray out of the circuit's
 * centroid: a centroid ray points the wrong way wherever the track is concave,
 * which on a street circuit is most of it.
 */
export function pointAndNormal(
  points: readonly Vec[], f: number, centroid: Vec, eps = 0.004,
): { p: [number, number]; n: [number, number] } {
  const p = pointAtFraction(points, f);
  const ahead = pointAtFraction(points, f + eps);
  const behind = pointAtFraction(points, f - eps);
  const tx = ahead[0] - behind[0], ty = ahead[1] - behind[1];
  const tl = Math.hypot(tx, ty) || 1;
  let nx = -ty / tl, ny = tx / tl;
  // Face away from the middle of the circuit.
  if (nx * (p[0] - centroid[0]) + ny * (p[1] - centroid[1]) < 0) { nx = -nx; ny = -ny; }
  return { p, n: [nx, ny] };
}
