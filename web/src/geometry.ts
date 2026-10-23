// Same edge numbering as dnb/engine/state.py: horizontal edges first, then vertical.

export interface EdgeGeom {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export function numEdges(rows: number, cols: number): number {
  return (rows + 1) * cols + rows * (cols + 1);
}

/** Edge index -> endpoints in dot coordinates (column, row). */
export function edgeGeom(rows: number, cols: number, edge: number): EdgeGeom {
  const numH = (rows + 1) * cols;
  if (edge < numH) {
    const r = Math.floor(edge / cols);
    const c = edge % cols;
    return { x1: c, y1: r, x2: c + 1, y2: r };
  }
  const k = edge - numH;
  const r = Math.floor(k / (cols + 1));
  const c = k % (cols + 1);
  return { x1: c, y1: r, x2: c, y2: r + 1 };
}
