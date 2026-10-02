// The spine's insurance: load the real woven file in jsdom and fire
// the game's own rules engine with the events of a real playthrough.
// Proves the story logic - the Evercan, the five lamps, the Beacon's
// condition - without walking there in a browser.
//
//   node tools/rules_test.mjs [path/to/lanternwake-*.html]

import { readFileSync, globSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";

const here = dirname(fileURLToPath(import.meta.url));
const builds = globSync(join(here, "..", "..", "..", "dist", "lanternwake-*.html"));
const file = process.argv[2] || builds[builds.length - 1];
const html = readFileSync(file, "utf8");

const dom = new JSDOM(html, {
  runScripts: "dangerously",
  pretendToBeVisual: true,
  url: "https://lanternwake.test/",   // an opaque origin has no localStorage
});
const w = dom.window;

// jsdom has no canvas: give the player the minimal 2D stub the engine's
// own harnesses use, before anything draws.
const stub = new Proxy({}, {
  get: (t, k) => (k === "canvas" ? {} : (t[k] ?? (() => stub))),
  set: () => true,
});
w.HTMLCanvasElement.prototype.getContext = () => stub;

// boot the game the way a player does: Begin (its handler settles on
// the next tick). The rules engine is built with the play surface.
w.document.getElementById("ts-enter").click();
await new Promise(r => setTimeout(r, 80));

let fails = 0;
function check(name, ok, detail = "") {
  console.log(`${ok ? "ok" : "FAIL"}  ${name}${detail ? `  [${detail}]` : ""}`);
  if (!ok) fails++;
}

const engine = w.VEFR_RULES_ENGINE;
check("the woven file carries the rules engine", !!engine);
check("40 rules are baked", (w.VEFR_RULES || []).length === 40, `${(w.VEFR_RULES || []).length}`);

// a fresh game, exactly as Begin builds it
let state = engine.newState({
  rules: w.VEFR_RULES, flags: w.VEFR_FLAGS,
  claims: w.VEFR_CLAIMS, people: w.VEFR_PEOPLE,
});

// 1. Begin: the Evercan is given and the orientation speaks
let out = engine.run(state, "starts", {});
const gave = out.actions.some(a => a.give === "the-evercan");
check("Begin gives the Evercan", gave);
check("Begin sets nothing on", Object.values(state.flags).every(v => !v));

// 2. walking to the causeway lamp without the can does nothing
state = engine.newState({ rules: w.VEFR_RULES, flags: w.VEFR_FLAGS,
  claims: w.VEFR_CLAIMS, people: w.VEFR_PEOPLE });
out = engine.run(state, "comes-near", { who: "the unlit causeway lamp", distance: 0 });
check("the lamp stays dark without the can",
      !state.flags["the-causeway-lamp-lit"] && out.fired.length === 0,
      `${out.fired.length} rules fired`);

// 3. with the can in the bag, the lamp lights
state = engine.newState({ rules: w.VEFR_RULES, flags: w.VEFR_FLAGS,
  claims: w.VEFR_CLAIMS, people: w.VEFR_PEOPLE });
engine.run(state, "starts", {});           // the Evercan is given
out = engine.run(state, "comes-near", { who: "the unlit causeway lamp", distance: 0 });
check("the causeway lamp lights", state.flags["the-causeway-lamp-lit"] === true,
      out.fired.map(f => f.id).join(","));
const token = out.actions.some(a => a.give === "wake-token");
check("lighting it gives a wake-token", token);
const spoke = out.actions.some(a => typeof a.say === "string" && /wick takes the oil/.test(a.say));
check("the narrator names the wick", spoke);

// 4. it fires once only
out = engine.run(state, "comes-near", { who: "the unlit causeway lamp", distance: 0 });
check("the lamp rule does not repeat", out.fired.length === 0);

// 5. the Beacon refuses to light on four lamps
state = engine.newState({ rules: w.VEFR_RULES, flags: w.VEFR_FLAGS,
  claims: w.VEFR_CLAIMS, people: w.VEFR_PEOPLE });
engine.run(state, "starts", {});
for (const lamp of ["the unlit causeway lamp", "the unlit ferry lamp",
                    "the unlit cliff lamp", "the unlit weald lamp"]) {
  engine.run(state, "comes-near", { who: lamp, distance: 0 });
}
out = engine.run(state, "comes-near", { who: "the Beacon door", distance: 0 });
check("the Beacon stays dark on four lamps",
      !state.flags["the-beacon-lit"] && out.fired.length === 0);

// 6. and lights on five
engine.run(state, "comes-near", { who: "the unlit chapel lamp", distance: 0 });
out = engine.run(state, "comes-near", { who: "the Beacon door", distance: 0 });
check("the Beacon lights on five lamps", state.flags["the-beacon-lit"] === true,
      out.fired.map(f => f.id).join(","));
check("the Beacon clears the weather",
      out.actions.some(a => a.weather === "clear"));

// 7. evidence moves a belief
state = engine.newState({ rules: w.VEFR_RULES, flags: w.VEFR_FLAGS,
  claims: w.VEFR_CLAIMS, people: w.VEFR_PEOPLE });
engine.run(state, "starts", {});
check("Aisling starts blaming the Guild",
      state.beliefs["aisling"] && state.beliefs["aisling"]["the-apprentice-burned-the-hall"].value === true,
      JSON.stringify(state.beliefs["aisling"]));
state.items["a-halfburnt-ledger"] = true;   // the rats' drop, picked up
out = engine.run(state, "comes-near", { who: "aisling", distance: 2 });
check("the ledger quiets Aisling's blame",
      state.beliefs["aisling"]["the-apprentice-burned-the-hall"].value === false,
      out.fired.map(f => f.id).join(","));

dom.window.close();
console.log("");
console.log(fails ? `${fails} FAILURES` : "rules test: the spine holds");
process.exit(fails ? 1 : 0);
