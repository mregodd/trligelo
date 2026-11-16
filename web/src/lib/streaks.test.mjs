// npm test. Node strips the types from streaks.ts itself, so no build step is needed.
import assert from "node:assert/strict";
import { test } from "node:test";

import { streaks } from "./streaks.ts";

const S = { G: 1, B: 0.5, M: 0 };
const run = (results) => [...results].map((r, i) => ({ t: "match", seq: i, s: S[r] }));
const notes = (events) => [...streaks(events)].map(([seq, s]) => `${seq}:${s.kind}${s.n}`);

test("wins and defeats in a row count from the third, and so does ending them", () => {
  assert.deepEqual(notes(run("GGGM")), ["2:wins3", "3:endedWins3"]);
  assert.deepEqual(notes(run("MMMB")), ["2:losses3", "3:endedLosses3"]);
});

test("runs with draws in them count from the fifth", () => {
  assert.deepEqual(notes(run("GBGBB")), ["4:unbeaten5"]);
  assert.deepEqual(notes(run("MBMBBG")), ["4:winless5", "5:endedWinless5"]);
  assert.deepEqual(notes(run("GBGBGM")), ["5:endedUnbeaten5"]);
});

test("adjustments between matches do not break a run", () => {
  const events = run("GGG");
  events.splice(2, 0, { t: "regression", seq: 99, d: -5 });
  assert.deepEqual(notes(events), ["2:wins3"]);
});
