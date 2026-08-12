# Prompt for ChatGPT — Go2 Robotics Workbook

Copy everything below the line into ChatGPT.

---

You are an expert instructional designer and curriculum writer for NSW (Australia) secondary school technology subjects. Create a **colourful, visually engaging student workbook** that teaches Stage 5 (Years 9–10) Computing Technology and Stage 6 (Years 11–12) Software Engineering students how to program a real robot — a Unitree Go2 Pro quadruped — using a specific existing Python application. I will give you the exact real capabilities of that application below; base all code examples, command names, and function names strictly on that reference material. Do not invent commands, functions, or APIs that aren't listed.

## Audience and curriculum alignment

Two groups will use this workbook, with different depth in the same chapters:

- **Stage 5 Computing Technology** (NESA *Computing Technology 7–10* syllabus, Years 9–10), especially the Stream 2 "Software Development" focus area **"Building mechatronic and automated systems."** These students need concrete, visual, low-friction entry points — block-based programming, guided exercises, lots of "try this and observe what happens."
- **Stage 6 Software Engineering** (NESA *Software Engineering 11–12* syllabus). Specifically:
  - **Year 11 — Programming Fundamentals, The Object-Oriented Paradigm, and Programming Mechatronics.** This project is a genuine mechatronics case study: sensors (camera, LIDAR), actuators (the robot's legs), a control class (`Go2ControlClient`), and closed-loop control.
  - **Year 12 — Secure Software Architecture, Software Automation, Software Engineering Project.** Use this project's safety design (speed caps, timeouts, validated inputs) as a secure-design case study, and the ML training pipeline as a software automation case study.

Write each chapter so a Stage 5 student can complete the block-based / guided-Python activities, and a Stage 6 student can go further into the underlying Python, the object-oriented design, and the engineering trade-offs. Use a clear visual marker to separate "Core" (both stages) from "Extension" (Stage 6 / advanced Stage 5) content.

**Important accuracy instruction:** Do not fabricate specific NESA syllabus outcome codes (e.g. "SE-11-03") — you may not have current, verified access to them. Instead write outcome descriptions in plain language and leave a clearly marked placeholder like `[Teacher: insert current NESA outcome code here]` wherever a specific code would normally go, so the teacher can fill in the verified code themselves.

## What this application actually does (ground truth — use only this)

The application is a Python project (`go2_webrtc_control`) that connects to a Unitree Go2 Pro over WebRTC via the robot's own WiFi hotspot. It is intentionally safety-limited: walk speed is hard-capped at 0.3 m/s, turn rate at 1.0 rad/s, and acrobatic commands are blocked outright. It does **not** have access to low-level joint/motor control (that requires different EDU-tier hardware and wiring) — this is a useful discussion point about hardware tiers and API design, not a gap to paper over.

**1. Core movement** (`go2_control/client.py`, `cli.py`) — a `Go2ControlClient` Python class with async methods: `balance_stand()`, `stand_up()`, `stand_down()`, `sit()`, `rise_sit()`, `stop_move()`, `recovery_stand()`, `move(forward, sideways, turn)`, `walk_for(...)`, `speed_level()`, `switch_gait()`, `set_body_height()`, `set_foot_raise_height()`, `pose()`, `euler_body_tilt()`, and gestures `hello()`, `content()`, `stretch()`, `heart_pose()`, `dance1()`, `dance2()`, `wallow()`, `scrape()`, `wiggle_hips()`. A command-line tool (`go2_control.cli`) offers the same actions plus named preset routines (`greet`, `calm-start`, `short-walk`, `reset`, `turn-left`, `turn-right`, `back-up-slowly`) and an interactive menu.

**2. A browser-based movement simulator** (`move_simulation.html`) that animates a routine's path/heading without needing the real robot — useful for planning before running on hardware.

**3. A drag-and-drop block editor** (`block_ide.html`, Blockly-based) covering nearly every capability below. Students snap blocks together; the real generated Python code is shown live next to the blocks. No live "run" button — students save and run the generated `.py` file themselves, which is a deliberate teaching point about reviewing code before executing it on physical hardware.

**4. Camera** (`camera_view.py`) — save JPEG snapshots or show a live preview from the robot's front camera.

**5. LIDAR** (`lidar_view.py`) — view and optionally record decoded LIDAR point-cloud messages.

**6. Telemetry** (`telemetry.py`) — read-only battery percentage, IMU orientation (roll/pitch/yaw), velocity, and odometry (position over time, loggable to CSV).

**7. Audio and LEDs** (`audio.py`, `experimental.py`) — list/play built-in sounds through the robot's speaker; set the status LED colour (with optional flashing), speaker volume, and screen/light brightness; toggle the robot's built-in obstacle avoidance on/off.

**8. Object detection and tracking (computer vision + ML)**:
   - `object_tracker.py` — uses a small pretrained YOLO model to detect everyday objects (person, sports ball, bottle, etc.) in the live camera feed and logs their position over time to CSV. Passive only — never moves the robot.
   - `lidar_tracker.py` — a simpler, fully explainable LIDAR-based tracker: calibrate an empty-room "background," then treat any new LIDAR data as a possible moving object, clustering it to find its position. Also passive only.

**9. Active following** (`follow.py`) — the one script where the robot actually moves based on what it sees: a proportional ("P") controller turns the robot toward a detected object and walks forward only when it's centred and not too close. Heavily guarded: validated speed limits, automatic stop if the object is lost for over a second, a hard maximum run time, and a printed safety warning before it starts.

**10. Training your own vision model** (`dataset_capture.py` → `train_classifier.py` → `recognize.py`) — capture your own labelled photos with the robot's camera, fine-tune a small image classifier on them (real supervised machine learning, not a canned demo), then run your own trained model live.

**11. Training a "follow" behaviour from demonstration** (`record_demo.py` → `train_follow_policy.py`) — record labelled examples of "what a human would do" given where an object is in frame, fit a small transparent linear regression model to that data (not a black box — students can read the resulting numbers), and load it into `follow.py` to compare a *learned* behaviour against the *hand-coded* one from item 9. This is a genuine, simplified introduction to behaviour cloning / imitation learning.

## Required structure

Design the workbook as a series of chapters/modules, one per capability area above (you may merge closely related items, e.g. camera + LIDAR viewing). For **each** chapter include, in this order:

1. **A colourful title banner concept** — describe the intended colour and icon for this chapter's header band (see design system below) so it can be laid out in a design tool.
2. **Learning intentions** — 2–4 plain-language "By the end of this chapter, you will be able to..." statements, tagged `[Core]` or `[Extension]`.
3. **Key vocabulary** — a short glossary box (5–8 terms) relevant to that chapter (e.g. for the ML chapters: *supervised learning*, *training data*, *overfitting*, *inference*).
4. **How it works** — a plain-language explanation with an accompanying diagram description (describe what the diagram should show; you don't need to draw it, just specify it clearly enough for a designer to create it).
5. **Walkthrough** — an annotated, accurate code or block example, using only the real names given above.
6. **Try it yourself** — a hands-on task with clear steps and a "what should happen" checkpoint.
7. **Challenge / Extension** — a harder task for Stage 6 or advanced Stage 5 students, explicitly building on the "Try it yourself" task.
8. **Safety check** — a short callout repeating the relevant safety rule (space required, speed caps, supervision, etc.) — every chapter that can move the robot must include this, styled to stand out.
9. **Reflection / discussion questions** — 2–3 questions connecting the activity to broader software engineering or ethical concepts (e.g. "Why does `follow.py` stop automatically if it loses the object, instead of continuing with its last command?"; "What are the risks and benefits of letting a robot make movement decisions from a machine learning model instead of fixed code?").

At the end of the workbook, include:
- A **glossary** consolidating all key vocabulary.
- A **command/function quick-reference table** (chapter, command, one-line description) — again, only real names from the reference material above.
- A **suggested assessment task** for Stage 5 and a separate one for Stage 6, each mapped to the relevant focus area/module named above, with a simple marking rubric (criteria + 3–4 achievement levels).
- An **ethics and safety discussion page** covering: physical safety around moving robots, privacy considerations of a robot with a camera, and the responsible-AI theme already built into this project (the workbook should specifically mention that this project deliberately limits robot autonomy — hard speed caps, automatic stop-on-lost-target, clipped model outputs — as a worked example of designing AI systems with bounded authority).

## Visual design system (describe this explicitly so a designer/Canva user can apply it)

- A distinct **accent colour per chapter category**: Movement = one colour, Sensing (camera/LIDAR/telemetry) = a second, Expression (audio/LED) = a third, AI/ML (tracking, training, following) = a fourth. Keep these consistent across the whole workbook so students learn to recognise category by colour.
- Recurring **icon + colour callout boxes** for: 💡 Key Idea, ⚠️ Safety Check, 🛠️ Try It Yourself, 🚀 Challenge, 🗒️ Vocabulary, 💬 Reflection — specify a consistent colour for each box type across all chapters.
- Friendly, energetic but not childish tone — appropriate for teenagers, not primary schoolers.
- Generous white space, short paragraphs, bulleted steps rather than dense prose, since this is a workbook students write in, not a textbook they only read.
- Suggest a simple robot/paw-print motif usable as a recurring graphic element.

## Output format

Produce the workbook content in clean Markdown with clear headings, so it can be pasted into a design tool (e.g. Canva, Google Docs) afterward. Include a table of contents at the top. Where you describe a diagram, banner, or graphic rather than being able to render it, use a clearly labelled `[DESIGN NOTE: ...]` block so it's obvious to the teacher what still needs to be created visually. Aim for enough depth that each chapter could fill a printed double-page spread — not just a paragraph.
