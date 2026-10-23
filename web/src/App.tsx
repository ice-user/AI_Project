import { useEffect, useState } from "react";
import { api, type Game } from "./api";
import { Board } from "./Board";

export default function App() {
  const [bots, setBots] = useState<string[]>(["random"]);
  const [bot, setBot] = useState("random");
  const [size, setSize] = useState(3);
  const [game, setGame] = useState<Game | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.listBots().then(setBots).catch((e) => setError(String(e)));
  }, []);

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

  const newGame = () => run(() => api.newGame({ rows: size, cols: size, bot }));
  const move = (edge: number) => game && run(() => api.move(game.id, edge));

  const you = game?.human_player ?? 0;
  const yourTurn = !!game && !game.is_over && game.current_player === you;

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
        {/* TODO(P5+P4): hint button + danger highlight, review screen after the game */}
      </section>

      {error && <p className="error">{error}</p>}

      {game && (
        <>
          <p className="status">
            <span className="p0">You {game.scores[you]}</span> ·{" "}
            <span className="p1">Bot {game.scores[1 - you]}</span> —{" "}
            {game.is_over
              ? game.winner === null
                ? "Draw!"
                : game.winner === you
                  ? "You win!"
                  : "Bot wins."
              : yourTurn
                ? "Your move"
                : "Bot is thinking…"}
          </p>
          <Board game={game} canMove={yourTurn && !busy} onMove={move} />
        </>
      )}
    </main>
  );
}
