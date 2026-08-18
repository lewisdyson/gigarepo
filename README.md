# The Adoption Quest

An 8-bit playable resume for Lewis Dyson, Product Marketing Manager.

Six zones, one per career chapter, walked in order. Each land starts drained of
colour because nobody there trusts you yet. You fill a Trust Meter by talking to
the skeptics, the palette warms, and the gate to the next land opens. The final
zone ends in a launch rather than a boss fight.

Play it, or press **Skip to resume** at any point for the plain version: stats,
full role history, portfolio links, and contact details.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The entire game. One self-contained file, no dependencies, no build step. |
| `make_face.py` | Generates the pixel portrait and the in-game sprites. Source of truth for the artwork. |
| `assets/` | Exported PNGs of the portrait and a sprite sheet of every view. |

## Running it

Open `index.html` in a browser. That is the whole process.

To serve it locally instead:

```
python3 -m http.server 8000
```

Then visit http://localhost:8000

## Editing the artwork

The sprites are plain text grids in `make_face.py`, one character per pixel,
mapped through a palette at the top of that file. Edit the grids, then:

```
python3 make_face.py
```

It validates that every row is the correct width, writes the PNGs into
`assets/`, and prints a report. It also writes `sprites.js`, which is the block
pasted into `index.html`. Editing the grids inside `index.html` directly works
too, but the Python file is where the width checks live.

## Deploying

Any static host works. For GitHub Pages, enable Pages in repository settings and
deploy from the default branch, root folder. The game is then served at
`https://<user>.github.io/<repo>/`.

The page is designed to be embedded in an iframe: it detects when it is framed,
takes keyboard focus on the first click, and adjusts its instructions
accordingly. That matters because until the frame has focus, arrow keys scroll
the host page instead of moving the character.

## Notes

Every number in the game is verified. Titles and date ranges match the written
resume exactly.
