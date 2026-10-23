// CONTRACT: mirrors dnb/server/schemas.py. Change both in the same PR.

export interface PlayedMove {
  player: number;
  edge: number;
}

export interface Game {
  id: string;
  rows: number;
  cols: number;
  bot: string;
  human_player: number;
  current_player: number;
  moves: PlayedMove[];
  box_owners: number[]; // -1 = unclaimed
  scores: number[];
  is_over: boolean;
  winner: number | null;
}

export interface NewGameRequest {
  rows?: number;
  cols?: number;
  bot?: string;
  level?: number | null;
  human_first?: boolean;
  player_id?: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  listBots: () => request<string[]>("/bots"),
  newGame: (req: NewGameRequest) =>
    request<Game>("/games", { method: "POST", body: JSON.stringify(req) }),
  move: (id: string, edge: number) =>
    request<Game>(`/games/${id}/move`, { method: "POST", body: JSON.stringify({ edge }) }),
  // TODO(P5): hint, review, stats once Persons 3 and 4 ship them.
};
