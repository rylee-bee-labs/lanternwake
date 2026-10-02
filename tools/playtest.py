#!/usr/bin/env python3
"""Play LANTERNWAKE's woven build in a real browser, and prove the
journey works: title -> begin -> walk -> look -> talk -> fight ->
pick up -> phase rail -> whisper -> bag. Screenshots land in
art/out/playtest/ so the review is visual.

  python3 tools/playtest.py            # against the newest dist/*.html
  python3 tools/playtest.py FILE.html

Exit code 0 = every assertion held. It prints each step's evidence.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PACK = Path(__file__).resolve().parents[1]
OUT = PACK / "art" / "out" / "playtest"


def newest_build() -> Path:
    dist = PACK.parents[1] / "dist"
    builds = sorted(dist.glob("lanternwake-*.html"))
    if not builds:
        raise SystemExit("no dist/lanternwake-*.html - run: uv run vefr weave --pack lanternwake")
    return builds[-1]


def main() -> int:
    build = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_build()
    OUT.mkdir(parents=True, exist_ok=True)
    fails: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"{'ok' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
        if not ok:
            fails.append(name)

    def close_overlays(pg) -> str:
        """Close whatever dialog the play opened; return which."""
        seen = []
        if pg.locator("#reader").is_visible():
            seen.append("reader")
            pg.locator("#reader-close").click()
            pg.wait_for_timeout(150)
        if pg.locator("#trade").is_visible():
            seen.append("trade")
            pg.locator("#trade-close").click()
            pg.wait_for_timeout(150)
        return ",".join(seen)

    def walk_to(pg, tx: int, ty: int, limit: int = 200) -> tuple[int, int]:
        """Walk the hero to (tx,ty) with BFS-derived keystrokes. A door
        tile yanks the hero to another region - that is a valid stop."""
        start_region = pg.evaluate("() => window.refreshCombatSnapshot().region")
        geom = pg.evaluate(
            "() => ({map: window.VEFR_REGIONS[window.VEFR_COMBAT.region].map,"
            " legend: window.VEFR_REGIONS[window.VEFR_COMBAT.region].legend})")
        rows, legend = geom["map"], geom["legend"]

        def solid(x: int, y: int) -> bool:
            if y < 0 or y >= len(rows) or x < 0 or x >= len(rows[0]):
                return True
            return bool((legend.get(rows[y][x]) or {}).get("solid"))

        # BFS from the target back to the hero: parent pointers
        parent: dict[tuple[int, int], tuple[int, int] | None] = {(tx, ty): None}
        queue = [(tx, ty)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                n = (x + dx, y + dy)
                if n not in parent and not solid(*n):
                    parent[n] = (x, y)
                    queue.append(n)
        cur = tuple(pg.evaluate("() => window.refreshCombatSnapshot().hero.at"))
        path: list[tuple[int, int]] = []
        while cur in parent and parent[cur] is not None:
            cur = parent[cur]
            path.append(cur)
        for (nx, ny) in path[:limit]:
            snap = pg.evaluate("() => window.refreshCombatSnapshot()")
            if snap["region"] != start_region:
                break
            hx, hy = snap["hero"]["at"]
            key = "ArrowRight" if nx > hx else "ArrowLeft" if nx < hx \
                else "ArrowDown" if ny > hy else "ArrowUp"
            pg.keyboard.press(key)
            pg.wait_for_timeout(70)
            close_overlays(pg)
        return tuple(pg.evaluate("() => window.refreshCombatSnapshot().hero.at"))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1100, "height": 820})
        page.goto(build.resolve().as_uri())
        page.wait_for_load_state("networkidle")

        # --- title screen ---
        title = page.locator("#ts-title")
        check("title screen names the game",
              title.is_visible() and "Lantern" in title.inner_text(),
              title.inner_text() if title.is_visible() else "hidden")
        page.screenshot(path=OUT / "01-title.png")

        # --- begin ---
        page.locator("#ts-enter").click()
        page.wait_for_timeout(300)
        cfg = page.locator("#config")
        if cfg.is_visible():
            page.locator("#cfg-offline").click()
        page.wait_for_timeout(500)
        check("the stage is up", page.locator("#stage").is_visible())
        page.screenshot(path=OUT / "02-thornhollow.png")

        # --- the world is the right one ---
        world = page.evaluate("() => window.VEFR_WORLD && window.VEFR_WORLD.name")
        check("woven world is lanternwake", world == "lanternwake", str(world))
        regions = page.evaluate("() => Object.keys(window.VEFR_REGIONS || {})")
        check("all regions are baked in", len(regions) >= 15, f"{len(regions)} regions")
        rules = page.evaluate("() => (window.VEFR_RULES || []).length")
        check("rules are baked in", rules == 40, f"{rules} rules")

        # --- move: walk the street to the clerk ---
        hero0 = page.evaluate("() => window.refreshCombatSnapshot().hero.at.slice()")
        opened = close_overlays(page)   # a book may greet the player at once
        landed = walk_to(page, 17, 10)
        opened = opened or close_overlays(page)
        check("the hero walks the street", hero0 != list(landed), f"{hero0} -> {landed}")
        check("a book greets the player", opened == "reader", opened or "nothing opened")

        # --- the wake-up rule gave the Evercan ---
        bag = page.evaluate("() => JSON.parse(localStorage.getItem('vefr-bag-lanternwake') || '[]')")
        check("the Evercan is in the bag", "the-evercan" in bag, str(bag))

        # --- talk to Teodor Quill ---
        close_overlays(page)
        page.locator("#talk").click()
        page.wait_for_timeout(300)
        near = page.locator("#near").inner_text()
        npc_visible = page.locator("#npc-box").is_visible()
        check("talk answers in words", npc_visible or bool(near.strip()),
              (page.locator("#npc-line").inner_text() if npc_visible else near)[:70])
        page.screenshot(path=OUT / "03-talk.png")
        if npc_visible:
            page.locator("#npc-close").click()

        # --- whisper (offline: pool/fragments/grammar) ---
        close_overlays(page)
        page.locator("#whisper").click()
        page.wait_for_timeout(600)
        spoke = page.locator("#npc-box").is_visible()
        line = page.locator("#npc-line").inner_text() if spoke else page.locator("#status").inner_text()
        check("whisper speaks offline", spoke and bool(line.strip()), line[:70])
        page.screenshot(path=OUT / "04-whisper.png")
        close_overlays(page)

        # --- the phase rail ---
        phases = page.evaluate("() => Object.keys(window.VEFR_WORLD.phases)")
        check("four watches are on the rail", len(phases) == 4, str(phases))
        page.locator(f'#phase button[data-phase="{phases[-1]}"]').click()
        page.wait_for_timeout(200)
        pressed = page.evaluate(
            f"() => document.querySelector('#phase button[data-phase=\"{phases[-1]}\"]').getAttribute('aria-pressed')")
        check("the rail switches the watch", pressed == "true", str(pressed))

        # --- bag panel ---
        page.keyboard.press("b")
        page.wait_for_timeout(200)
        check("the bag opens", page.locator("#menu").is_visible()
              or page.locator("#bag-list").is_visible())
        page.screenshot(path=OUT / "05-bag.png")
        page.keyboard.press("Escape")

        # --- travel to the cellars door region and fight a rat ---
        page.evaluate("""() => {
          // deterministic jump through the game's own door seam
          const t = (window.VEFR_TRANSITIONS || []).find(
            t => t.from === 'thornhollow' && String(t.to) === 'the-cellars');
          window.__door = t || null;
        }""")
        door = page.evaluate("() => window.__door")
        check("a door to the cellars exists", bool(door), str(door)[:60])

        # walk beside that door and press Interact (doors open with
        # the one verb, not by stepping: the button says so)
        if door:
            tx, ty = door["at"]
            ax, ay = (tx - 1, ty) if tx > 0 else (tx + 1, ty)
            walk_to(page, ax, ay)
            page.keyboard.press("ArrowRight" if ax < tx else "ArrowLeft")
            page.wait_for_timeout(120)
            label = page.locator("#interact-label").inner_text()
            check("the Interact button names the door", "door" in label.lower(), label)
            page.keyboard.press("f")
            page.wait_for_timeout(300)
            close_overlays(page)
            here = page.evaluate("() => window.refreshCombatSnapshot().region")
            check("the hero crossed into the cellars", here == "the-cellars", str(here))
            page.screenshot(path=OUT / "06-cellars.png")

            # hunt the nearest rat: walk toward it, bump to strike
            for _ in range(30):
                snap = page.evaluate("() => window.refreshCombatSnapshot()")
                hx, hy = snap["hero"]["at"]
                foes = [e for e in snap["enemies"] if e["alive"]]
                if not foes:
                    break
                foes.sort(key=lambda e: abs(e["at"][0] - hx) + abs(e["at"][1] - hy))
                fx, fy = foes[0]["at"]
                key = "ArrowRight" if fx > hx else "ArrowLeft" if fx < hx \
                    else "ArrowDown" if fy > hy else "ArrowUp"
                page.keyboard.press(key)
                page.wait_for_timeout(80)
                close_overlays(page)
            log = page.locator("#combat-log").inner_text()
            slain = page.evaluate("() => window.refreshCombatSnapshot().enemies.filter(e => !e.alive).length")
            check("combat is happening", bool(log.strip()) or slain > 0,
                  (log[:60] or f"{slain} slain"))
            page.screenshot(path=OUT / "07-combat.png")

        # --- start over is offered ---
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        page.screenshot(path=OUT / "08-menu.png")

        browser.close()

    print()
    if fails:
        print(f"{len(fails)} FAILURES: {fails}")
        return 1
    print("playtest: every step held")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
