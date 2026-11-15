# Deck handoff (2026-11-15)

## Ground rules
- **Edit these scripts, never `pitch-deck.html`.** Sources are in `deck/`; nearly all slide content and data is in `deck/3-posters-rest.js`.
- **Rebuild:** `bash deck/build.sh`. It needs Node from nvm: `export PATH="$HOME/.nvm/versions/node/v24.11.0/bin:$PATH"`, and must run outside the sandbox. It now stops if any step fails.
- **Screenshot one slide:** headless Edge outside the sandbox. Change `#N` to the slide number.
  `"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --headless=new --disable-gpu --hide-scrollbars --window-size=1920,1080 --virtual-time-budget=4000 --screenshot=out.png "file://$PWD/pitch-deck.html#N"`
- **Pushing:** directly to `main` (no PRs). Only one person edits the deck at a time. Last session a commit (`5844e6c`) swept in someone's half-finished edits.
- **Judging weights** (`REQUIREMENTS.md`): gap 30, meaningful difficulty 30, reward integrity 25, craft 15. The video must be 2:00 or shorter. The submission also needs a PDF of the deck.

## Current deck (as of `5844e6c`)
| # | Slide | Source | Judging point |
|---|---|---|---|
| 1 | Can AI take our jobs? | `2-posters-1-2.js` | hook |
| 2 | A known design is not a working setup | `2-posters-1-2.js` | why this setting |
| 3 | Finding time zero means scanning for one narrow spike | `p7` | task + fairness |
| 4 | The agent controls a physics lab through MCP | `p4` | environment |
| 5 | Scored on physics (formula + bars) | `p8` | reward integrity |
| 6 | Average score of models | `p5` | gap |
| 7 | Common mistakes (4 panels, no captions) | `p6` | meaningful difficulty |
| 8 | One command (shows only the site link) | `p9` | craft |
| 9 | Agents cut coding to hours. Lab work is next. | `p10` | takeaway |
| 10–13 | Backup slides | `base-v2.html` | — |

The order is set at the line `html = html.slice(0, start) + [p7, p4, p8, p5, p6, p9, p10]...`. The task slide (`p3`, two pulses) is defined but no longer shown.

## Data we have (today's grader)
- **Scripted reference, seeds 1–10:** Level 1 averages 0.929 (min 0.923), Level 2 averages 0.928. Seed 1 at Level 2 scores 0.923.
- **Baselines:** do-nothing 0.000; stop-early 0.199.
- **Gemini runs (Level 1 Harbor, archived and replayable at kakitkelvinho.github.io/gss):**
  - Gemini 3.1 Pro: 0.000 × 4. It never got both beams onto the sample; see `docs/gemini-pro-results.md`.
  - Gemini 3.8 Flash: 0.185 and 0.199.
  - Gemini 4 Hydrogen: 0.200.
  - Gemini 4 Carbon: 0 tool calls (a thinking-budget harness problem), so it's excluded.
- **Blind Claude playthroughs, Level 2, seed 1** (command-line tool, *not Harbor*, not archived):

  | Player | Score | eta | Cost | Lab time | Outcome |
  |---|---|---|---|---|---|
  | p1 | 0.905 | 0.975 | €10,650 | 48% | found time zero |
  | p2 | 0.197 | 0 | €9,550 | 95% | missed time zero by 6.4 ps |
  | p3 | 0.931 | 0.987 | €8,550 | 49% | found time zero |

  The average is 0.678.
  - **p2's failure:** it tried the wrong 90° diagnostic, GaN plus a filter. It ran short of time, so it used short integrations, then submitted at a tape-measure guess.
  - **Friction all three named:** you can't see 1300 nm without the €6,500 InGaAs camera, and no doc says which overlap diagnostic to use for a 90° crossing. All three chose GaP.
  - **Friction two of three named:** the GaP peak is weak (about +350 on 1,500 counts), and the photodiode and tape-measure estimates of time zero are off by 1–3 mm.
  - **Friction p3 named:** knob responses are undocumented and uneven, and `ir_card(part="sample")` doesn't show the focus.

## Problems to fix, by priority
1. **The results slide (6) lost its context in the last edit.**
   - The stop-early line and the footnote were removed. Nothing on the slide now says the Claude row is Level 2, played through the command-line tool rather than Harbor, with scores 0.905, 0.197 and 0.931.
   - Put a footnote back, and the 0.2 stop-early line too, because it's what makes the Gemini bars mean something.
   - "Average score of models" is a label, not a claim. Consider "8 of 10 agent runs never found time zero", which is true but six of those are Gemini runs on Level 1.
2. **The gap story is honest only as an average.**
   - Claude matched or beat the reference in 2 of 3 runs, so "consistently below" holds for Gemini only.
   - Wait for the friend's **Harbor** Claude runs; judges rerun through Harbor. Then update the Claude row and say so on the slide.
3. **The common mistakes slide (7) has no captions.**
   - The panels still show Flash's failures: 46 ps late, short integration, never blocked an arm, €4,030 over budget.
   - Without captions or a voice-over the judges can't connect a mistake to a decision, which is what full marks for meaningful difficulty require.
   - Restore the captions, or rebuild the slide around p2 (the strongest model failing on real decisions: diagnostic choice, then time, then integration, then guessing). The speaker note still describes Flash.
4. **Without the task slide, nobody says what the goal is.**
   - Slide 3 opens on "time zero" without saying that two pulses must meet at the same spot and time.
   - Either bring back `p3`, or add one line of small text to slide 3.
5. **Scoring slide (5): the exploit list is gone.**
   - The † footnote listed absurd arguments, 100,000 mirrors, call spam, and verifier calls without the token. It's the slide's evidence for reward integrity (25 points).
   - Keep the formula, and put a one-line version of the list back.
6. **The command slide (8) no longer shows "77 tests · fixed seeds".** Craft points are about reproducing results, so put back a short line.
7. **Takeaway (9):** fine as it is; the bars were removed on purpose. Add the repo link if slide 8 doesn't carry it.
8. **Video timing:** add up the `~N s.` values in the speaker notes; the total must be 2:00 or shorter. Press V for the video cut and N for notes.
9. **Backup slide "Evidence still to collect":** update once the Harbor Claude runs exist.

## Fix outside the deck (it affects the meaningful-difficulty score)
- **Document knob behaviour** in the mount manuals (`sim/catalogue.py`): sign and step size per knob. Blind players have flagged it twice, and a judge could call it withheld information.
- **Optional:** a line in the sample manual saying that at Level 2 (90° crossing) sum-frequency in BBO can't phase-match. Without it, choosing the diagnostic stays a pure physics decision. That's arguably fair, but p2 lost the run to it.

## After that
- Export the PDF: open the deck online so the fonts load, then Ctrl/Cmd+P.
- Record the video (the friend).
- Decide whether to publish the blind Claude logs. The Level 1 logs are in `/Users/hok5/Documents/gss-fixes/runs/blind-claude-2026-11-15/`; the friend has the Level 2 logs.
- Stretch goal, not started: train a smaller model on GSS experience. It's also the tiebreaker.
