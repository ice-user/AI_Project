import { useEffect, useState } from "react";
import { api, type Game, type Review } from "./api";
import { Board } from "./Board";
import { boxEdges } from "./geometry";

/** The game as it stood just before move `ply`, rebuilt from the move list. */
function positionBefore(game: Game, ply: number): Game {
  const moves = game.moves.slice(0, ply);
  const drawnAt = new Map(moves.map((m, i) => [m.edge, i]));
  const scores = [0, 0];
  const box_owners = game.box_owners.map((_, b) => {
    const edges = boxEdges(game.rows, game.cols, b);
    if (!edges.every((e) => drawnAt.has(e))) return -1;
    const owner = moves[Math.max(...edges.map((e) => drawnAt.get(e)!))].player;
    scores[owner] += 1;
    return owner;
  });
  return {
    ...game,
    moves,
    box_owners,
    scores,
    current_player: game.moves[ply].player,
    is_over: false,
    winner: null,
  };
}

export default function App() {
  const [bots, setBots] = useState<string[]>(["random"]);
  const [bot, setBot] = useState("random");
  const [size, setSize] = useState(3);
  const [game, setGame] = useState<Game | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [hintEdge, setHintEdge] = useState<number | null>(null);
  const [showDanger, setShowDanger] = useState(false);
  const [danger, setDanger] = useState<number[]>([]);
  const [review, setReview] = useState<Review | null>(null);
  const [selected, setSelected] = useState<number | null>(null); // ply of the reviewed move shown

  useEffect(() => {
    api.listBots().then(setBots).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    setHintEdge(null);
    setDanger([]);
    if (!game || !showDanger || game.is_over) return;
    let live = true;
    api
      .danger(game.id)
      .then((d) => live && setDanger(d.edges))
      .catch((e) => setError(String(e)));
    return () => {
      live = false;
    };
  }, [game, showDanger]);

  const gameId = game?.id;
  const gameOver = game?.is_over ?? false;
  useEffect(() => {
    setReview(null);
    setSelected(null);
    if (!gameId || !gameOver) return;
    let live = true;
    api
      .review(gameId)
      .then((r) => live && setReview(r))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      live = false;
    };
  }, [gameId, gameOver]);

  async function run(action: () => Promise<Game>) {
    setBusy(true);
    setError(null);
    try {
      setGame(await action());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function showHint() {
    if (!game) return;
    setBusy(true);
    setError(null);
    try {
      setHintEdge((await api.hint(game.id)).move);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const newGame = () => run(() => api.newGame({ rows: size, cols: size, bot }));
  const move = (edge: number) => game && run(() => api.move(game.id, edge));

  const you = game?.human_player ?? 0;
  const yourTurn = !!game && !game.is_over && game.current_player === you;

  const reviewed = review?.moves.find((m) => m.ply === selected);
  const shown = game && reviewed ? positionBefore(game, reviewed.ply) : game;
  const marks = new Map<number, string>();
  if (reviewed) {
    if (reviewed.best_move !== reviewed.move) marks.set(reviewed.best_move, "best");
    marks.set(reviewed.move, reviewed.label);
  } else {
    danger.forEach((e) => marks.set(e, "danger"));
    if (hintEdge !== null) marks.set(hintEdge, "hint");
  }
  const counts = (["good", "okay", "mistake"] as const).map(
    (label) => `${review?.moves.filter((m) => m.label === label).length ?? 0} ${label}`,
  );

  return (
    <main>
      <h1>
        Dots and Boxes <span className="accent">AI</span>
      </h1>

      <section className="controls">
        {/* TODO(P5+P3): difficulty picker (levels 1-5 + "auto") instead of raw bot specs */}
        <label>
          Bot{" "}
          <select value={bot} onChange={(e) => setBot(e.target.value)}>
            {bots.map((b) => (
              <option key={b}>{b}</option>
            ))}
          </select>
        </label>
        <label>
          Size{" "}
          <select value={size} onChange={(e) => setSize(Number(e.target.value))}>
            {[2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n}×{n}
              </option>
            ))}
          </select>
        </label>
        <button onClick={newGame} disabled={busy}>
          New game
        </button>
        <button onClick={showHint} disabled={!yourTurn || busy}>
          Hint
        </button>
        <label>
          <input
            type="checkbox"
            checked={showDanger}
            onChange={(e) => setShowDanger(e.target.checked)}
          />{" "}
          Show danger
        </label>
      </section>

      {error && <p className="error">{error}</p>}

      {game && shown && (
        <>
          <p className="status">
            <span className="p0">You {shown.scores[you]}</span> ·{" "}
            <span className="p1">Bot {shown.scores[1 - you]}</span> —{" "}
            {reviewed
              ? `Before move ${reviewed.ply + 1}`
              : game.is_over
                ? game.winner === null
                  ? "Draw!"
                  : game.winner === you
                    ? "You win!"
                    : "Bot wins."
                : yourTurn
                  ? busy
                    ? "Thinking…"
                    : "Your move"
                  : "Bot is thinking…"}
          </p>
          <Board game={shown} canMove={yourTurn && !busy && !reviewed} onMove={move} marks={marks} />
          <p className="legend">
            {reviewed
              ? reviewed.best_move === reviewed.move
                ? "Your move, coloured by its label. It was the best move here."
                : "Your move, coloured by its label. Dashed green: the better move."
              : "Dotted green: hint. Faint red: lines that leave a box with 3 sides."}
          </p>
        </>
      )}

      {game?.is_over && (
        <section className="review">
          <h2>Review</h2>
          {!review ? (
            <p>Reviewing your moves…</p>
          ) : (
            <>
              <p className="legend">{counts.join(" · ")}. Click a move to see it on the board.</p>
              <ol>
                {review.moves.map((m) => (
                  <li key={m.ply}>
                    <button
                      className={m.ply === selected ? "row selected" : "row"}
                      onClick={() => setSelected(m.ply === selected ? null : m.ply)}
                    >
                      <span className={`badge ${m.label}`}>{m.label}</span> Move {m.ply + 1}
                      {m.boxes_taken > 0 && ` · took ${m.boxes_taken}`}
                      {m.boxes_given_away > 0 && ` · gave away ${m.boxes_given_away}`}
                    </button>
                    {m.explanation && <p className="explanation">{m.explanation}</p>}
                  </li>
                ))}
              </ol>
            </>
          )}
        </section>
      )}
    </main>
  );
}
