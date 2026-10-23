import type { Game } from "./api";
import { edgeGeom, numEdges } from "./geometry";

const GAP = 70; // pixels between dots
const PAD = 20;
const PLAYER_COLORS = ["var(--p0)", "var(--p1)"];

interface Props {
  game: Game;
  canMove: boolean;
  onMove: (edge: number) => void;
}

export function Board({ game, canMove, onMove }: Props) {
  const { rows, cols } = game;
  const drawnBy = new Map(game.moves.map((m) => [m.edge, m.player]));
  const lastEdge = game.moves.at(-1)?.edge;
  const px = (v: number) => PAD + v * GAP;

  return (
    <svg
      className="board"
      viewBox={`0 0 ${2 * PAD + cols * GAP} ${2 * PAD + rows * GAP}`}
      role="img"
      aria-label="Dots and Boxes board"
    >
      {game.box_owners.map((owner, b) =>
        owner < 0 ? null : (
          <rect
            key={`box-${b}`}
            x={px(b % cols) + 6}
            y={px(Math.floor(b / cols)) + 6}
            width={GAP - 12}
            height={GAP - 12}
            rx={6}
            fill={PLAYER_COLORS[owner]}
            opacity={0.85}
          />
        ),
      )}

      {Array.from({ length: numEdges(rows, cols) }, (_, e) => {
        const g = edgeGeom(rows, cols, e);
        const player = drawnBy.get(e);
        const drawn = player !== undefined;
        const line = { x1: px(g.x1), y1: px(g.y1), x2: px(g.x2), y2: px(g.y2) };
        return (
          <g key={`edge-${e}`}>
            <line
              {...line}
              className={drawn ? "edge drawn" : "edge"}
              // Inline style, not the stroke attribute: CSS (.edge) would override the attribute.
              style={drawn ? { stroke: PLAYER_COLORS[player] } : undefined}
              strokeWidth={e === lastEdge ? 9 : 6}
            />
            {!drawn && canMove && (
              // Wide invisible hit area so lines are easy to click.
              <line {...line} className="edge-hit" onClick={() => onMove(e)} />
            )}
          </g>
        );
      })}

      {Array.from({ length: (rows + 1) * (cols + 1) }, (_, d) => (
        <circle
          key={`dot-${d}`}
          cx={px(d % (cols + 1))}
          cy={px(Math.floor(d / (cols + 1)))}
          r={6}
          className="dot"
        />
      ))}
    </svg>
  );
}
