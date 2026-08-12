# Next Session — Open Items

Status as of 2026-08-12. Everything below is unfinished business from the first full hardware bring-up session, not a general roadmap.

## Do first

- [ ] **Post the GitHub issue** about the intermittent `Move`/walking behavior. Draft is at `scratch_github_issue_draft.md` in the project root (gitignored, local-only — not in the repo). Post it to `legion1581/unitree_webrtc_connect` (the maintainer there answered a related `SwitchGait` question directly and clearly knows this protocol).
- [ ] **Power cycle the robot** (full off/on, not just an app service restart) before the next testing session — LIDAR reads went from reliable to consistently failing by the end of this session after ~40+ WebRTC reconnects and a lot of mode-switching experimentation. Worth starting the next session from a clean boot.

## Known unresolved issue (robot-side, not a code bug)

`Move` (walking/turning) is intermittently unreliable: identical code, commands, and timing sometimes produces real walking and sometimes just a lean, with no code-level difference found between successful and failed attempts. Extensively diagnosed this session (mode-switching, obstacle avoidance, no-reply vs request/response send patterns, physical-remote comparison) — see `CLAUDE.md`'s Architecture section for the short version, or the GitHub issue draft for the full writeup. Don't re-diagnose from scratch — pick up from the issue draft if revisiting.

## Pipelines built but never run against real hardware

These were coded and documented in `STUDENT_TUTORIAL.md` but not actually exercised on the robot this session — worth a real test pass before relying on them for a class:

- [ ] `dataset_capture.py` → `train_classifier.py` → `recognize.py` (the full "train your own vision model" loop, Part 15)
- [ ] `record_demo.py` → `train_follow_policy.py` (the "train a follow behavior from demonstration" loop, Part 16)
- [ ] `follow.py` (autonomous following) — only worth testing once walking is reliable again, since it depends on `Move`
- [ ] `pynput_teleop.py` (needs a one-time macOS Accessibility permission grant, untested this session)
- [ ] `vr_bridge.py` / `vr_webrtc.py` — optional, needs a Quest headset to test meaningfully

## Distribution follow-through

- [ ] Zip `dist_bundle/` and attach it to a GitHub Release (tag `v0.1.0`) so students can download without touching git — see the detailed steps from this session's chat if needed.
- [ ] `install_mac.sh` has only been verified in an isolated venv on this same dev machine — worth a real test on a second, genuinely different Mac before handing it to a full class.
