    let routines = {
      "demo.py": [
        { label: "speed_level(0)", type: "note", duration: 0.8, pose: "ready" },
        { label: "balance_stand (1002)", type: "balance", duration: 1.0, pose: "balance" },
        { label: "stand_up (1004)", type: "stand", duration: 1.0, pose: "stand" },
        { label: "content wag (1022)", type: "wag", duration: 1.0, pose: "wag" },
        { label: "walk_for(0.1, 1.5)", type: "walk", duration: 1.5, forward: 0.1, turn: 0.0, pose: "walk" },
        { label: "stop_move (1003)", type: "stop", duration: 0.8, pose: "stop" }
      ],
      "stand_wag_sit_example.py": [
        { label: "stand_up (1004)", type: "stand", duration: 2.0, pose: "stand" },
        { label: "content wag (1022)", type: "wag", duration: 2.0, pose: "wag" },
        { label: "sit (1009)", type: "sit", duration: 2.0, pose: "sit" }
      ],
      "repeat_tilt_sit.py": [
        { label: "tilt right", type: "tilt", duration: 1.0, roll: 12, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -12, pose: "tilt" },
        { label: "tilt right", type: "tilt", duration: 1.0, roll: 12, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -12, pose: "tilt" },
        { label: "tilt right", type: "tilt", duration: 1.0, roll: 12, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -12, pose: "tilt" },
        { label: "sit (1009)", type: "sit", duration: 2.0, pose: "sit" }
      ],
      "square_walk_sit.py": [
        { label: "stand_up (1004)", type: "stand", duration: 2.0, pose: "stand" },
        { label: "side 1 walk", type: "walk", duration: 3.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "turn 90", type: "walk", duration: 1.8, forward: 0.0, turn: 0.25, pose: "turn" },
        { label: "side 2 walk", type: "walk", duration: 3.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "turn 90", type: "walk", duration: 1.8, forward: 0.0, turn: 0.25, pose: "turn" },
        { label: "side 3 walk", type: "walk", duration: 3.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "turn 90", type: "walk", duration: 1.8, forward: 0.0, turn: 0.25, pose: "turn" },
        { label: "side 4 walk", type: "walk", duration: 3.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "turn 90", type: "walk", duration: 1.8, forward: 0.0, turn: 0.25, pose: "turn" },
        { label: "sit (1009)", type: "sit", duration: 2.0, pose: "sit" }
      ],
      "walk_turn_walk_sit.py": [
        { label: "stand_up (1004)", type: "stand", duration: 2.0, pose: "stand" },
        { label: "walk forward", type: "walk", duration: 3.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "walk + turn", type: "walk", duration: 2.0, forward: 0.3, turn: 0.2, pose: "turn" },
        { label: "walk forward", type: "walk", duration: 3.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "stop_move (1003)", type: "stop", duration: 0.8, pose: "stop" },
        { label: "sit (1009)", type: "sit", duration: 2.0, pose: "sit" }
      ],
      "performance_routine.py": [
        { label: "sit", type: "sit", duration: 1.0, pose: "sit" },
        { label: "stand_up", type: "stand", duration: 2.0, pose: "stand" },
        { label: "tilt right", type: "tilt", duration: 1.0, roll: 12, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -12, pose: "tilt" },
        { label: "tilt right", type: "tilt", duration: 1.0, roll: 12, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -12, pose: "tilt" },
        { label: "stretch", type: "stretch", duration: 2.0, pose: "stretch" },
        { label: "walk forward", type: "walk", duration: 4.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "walk arc", type: "walk", duration: 2.5, forward: 0.3, turn: 0.2, pose: "turn" },
        { label: "walk forward", type: "walk", duration: 4.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "hello", type: "hello", duration: 2.0, pose: "hello" },
        { label: "stop", type: "stop", duration: 0.5, pose: "stop" },
        { label: "sit", type: "sit", duration: 2.0, pose: "sit" }
      ],
      "pynput_teleop.py (sample session)": [
        { label: "stand_up (1004)", type: "stand", duration: 2.0, pose: "stand" },
        { label: "W held", type: "walk", duration: 2.0, forward: 0.3, turn: 0.0, pose: "walk" },
        { label: "A held", type: "walk", duration: 1.2, forward: 0.0, turn: 0.3, pose: "turn" },
        { label: "D held", type: "walk", duration: 1.2, forward: 0.0, turn: -0.3, pose: "turn" },
        { label: "S held", type: "walk", duration: 1.8, forward: -0.3, turn: 0.0, pose: "walk" },
        { label: "Space", type: "stop", duration: 0.8, pose: "stop" },
        { label: "Q", type: "sit", duration: 2.0, pose: "sit" }
      ],
      "cli.py routine:greet": [
        { label: "balance_stand", type: "balance", duration: 1.0, pose: "balance" },
        { label: "hello", type: "hello", duration: 1.0, pose: "hello" },
        { label: "content", type: "wag", duration: 1.0, pose: "wag" },
        { label: "stop", type: "stop", duration: 0.8, pose: "stop" }
      ],
      "cli.py routine:short-walk": [
        { label: "speed_level(0)", type: "note", duration: 0.7, pose: "ready" },
        { label: "balance_stand", type: "balance", duration: 1.0, pose: "balance" },
        { label: "walk_for_default", type: "walk", duration: 2.0, forward: 0.1, turn: 0.0, pose: "walk" },
        { label: "stop", type: "stop", duration: 0.8, pose: "stop" }
      ]
    };

    const canvas = document.getElementById("simCanvas");
    const ctx = canvas.getContext("2d");

    const routineSelect = document.getElementById("routine");
    const speedSlider = document.getElementById("speed");
    const playBtn = document.getElementById("play");
    const pauseBtn = document.getElementById("pause");
    const resetBtn = document.getElementById("reset");
    const timeline = document.getElementById("timeline");

    const statStep = document.getElementById("stat-step");
    const statPose = document.getElementById("stat-pose");
    const statPos = document.getElementById("stat-pos");
    const statHeading = document.getElementById("stat-heading");
    const routineLabel = document.getElementById("routineLabel");
    const badge = document.getElementById("badge");

    const PX_PER_M = 95;
    const TAU = Math.PI * 2;

    const sim = {
      running: false,
      speed: 1,
      routineName: "demo.py",
      steps: [],
      stepIndex: 0,
      stepT: 0,
      worldT: 0,
      x: 0,
      y: 0,
      heading: 0,
      rollDeg: 0,
      pose: "idle",
      tailPhase: 0,
      gaitPhase: 0,
      trail: [{ x: 0, y: 0 }],
      complete: false
    };

    function readNumber(text, name, fallback) {
      const match = text.match(new RegExp(`${name}\\s*=\\s*([-+]?[0-9]*\\.?[0-9]+)`));
      return match ? Number(match[1]) : fallback;
    }

    function readString(text, name, fallback) {
      const match = text.match(new RegExp(`${name}\\s*=\\s*"([^"]+)"`));
      return match ? match[1] : fallback;
    }

    function parseClientCalls(text) {
      const steps = [];
      const callRegex = /await\s+client\.(\w+)\(([^)]*)\)/g;
      let match;

      while ((match = callRegex.exec(text)) !== null) {
        const method = match[1];
        const args = match[2];

        if (method === "speed_level") {
          steps.push({ label: `speed_level(${args.trim() || "0"})`, type: "note", duration: 0.7, pose: "ready" });
        } else if (method === "balance_stand") {
          steps.push({ label: "balance_stand", type: "balance", duration: 1.0, pose: "balance" });
        } else if (method === "stand_up") {
          steps.push({ label: "stand_up", type: "stand", duration: 1.4, pose: "stand" });
        } else if (method === "sit") {
          steps.push({ label: "sit", type: "sit", duration: 2.0, pose: "sit" });
        } else if (method === "content") {
          steps.push({ label: "content", type: "wag", duration: 1.2, pose: "wag" });
        } else if (method === "hello") {
          steps.push({ label: "hello", type: "hello", duration: 1.2, pose: "hello" });
        } else if (method === "stretch") {
          steps.push({ label: "stretch", type: "stretch", duration: 1.8, pose: "stretch" });
        } else if (method === "stop_move") {
          steps.push({ label: "stop_move", type: "stop", duration: 0.8, pose: "stop" });
        } else if (method === "walk_for") {
          const parts = args.split(",").map((v) => v.trim());
          const forward = Number(parts[0] || 0.1);
          const durationMatch = args.match(/duration_s\s*=\s*([-+]?[0-9]*\.?[0-9]+)/);
          const turnMatch = args.match(/turn_rps\s*=\s*([-+]?[0-9]*\.?[0-9]+)/);
          const duration = durationMatch ? Number(durationMatch[1]) : 2.0;
          const turn = turnMatch ? Number(turnMatch[1]) : 0.0;
          steps.push({
            label: `walk_for(${forward.toFixed(2)}, ${duration.toFixed(1)}s)`,
            type: "walk",
            duration,
            forward,
            turn,
            pose: Math.abs(turn) > 0.01 ? "turn" : "walk"
          });
        } else if (method === "walk_for_default") {
          const durationMatch = args.match(/duration_s\s*=\s*([-+]?[0-9]*\.?[0-9]+)/);
          const duration = durationMatch ? Number(durationMatch[1]) : 2.0;
          steps.push({ label: `walk_for_default(${duration.toFixed(1)}s)`, type: "walk", duration, forward: 0.1, turn: 0.0, pose: "walk" });
        }
      }

      return steps;
    }

    function parseSquareWalk(text) {
      const walkSpeed = readNumber(text, "FORWARD_SPEED_MPS", 0.3);
      const walkDuration = readNumber(text, "FORWARD_WALK_SECONDS", 3.0);
      const turnRate = readNumber(text, "TURN_RATE_RPS", 0.25);
      const turnDuration = readNumber(text, "TURN_DURATION_SECONDS", 1.8);
      const steps = [{ label: "stand_up", type: "stand", duration: 2.0, pose: "stand" }];

      for (let i = 0; i < 4; i += 1) {
        steps.push({ label: `side ${i + 1} walk`, type: "walk", duration: walkDuration, forward: walkSpeed, turn: 0.0, pose: "walk" });
        steps.push({ label: "turn 90", type: "walk", duration: turnDuration, forward: 0.0, turn: turnRate, pose: "turn" });
      }

      steps.push({ label: "sit", type: "sit", duration: 2.0, pose: "sit" });
      return steps;
    }

    function parseWalkTurnWalk(text) {
      const speed = readNumber(text, "FORWARD_SPEED_MPS", 0.3);
      const first = readNumber(text, "FIRST_WALK_SECONDS", 3.0);
      const turnDur = readNumber(text, "TURN_SECONDS", 2.0);
      const second = readNumber(text, "SECOND_WALK_SECONDS", 3.0);
      const dir = readString(text, "TURN_DIRECTION", "left").toLowerCase();
      const turnMag = Math.abs(readNumber(text, "TURN_RATE_RPS", 0.2));
      const turn = dir === "right" ? -turnMag : turnMag;

      return [
        { label: "stand_up", type: "stand", duration: 2.0, pose: "stand" },
        { label: "walk forward", type: "walk", duration: first, forward: speed, turn: 0.0, pose: "walk" },
        { label: "walk + turn", type: "walk", duration: turnDur, forward: speed, turn, pose: "turn" },
        { label: "walk forward", type: "walk", duration: second, forward: speed, turn: 0.0, pose: "walk" },
        { label: "stop_move", type: "stop", duration: 0.8, pose: "stop" },
        { label: "sit", type: "sit", duration: 2.0, pose: "sit" }
      ];
    }

    function parseRepeatTilt(text) {
      const repeats = Math.max(1, Math.floor(readNumber(text, "NUM_REPEATS", 3)));
      const side = readString(text, "TURN_SIDE", "right").toLowerCase();
      const angle = readNumber(text, "TILT_ANGLE_DEGREES", 12.0);
      const steps = [];

      for (let i = 0; i < repeats; i += 1) {
        steps.push({ label: `tilt ${side}`, type: "tilt", duration: 1.0, roll: side === "right" ? angle : -angle, pose: "tilt" });
        steps.push({ label: `tilt ${side === "right" ? "left" : "right"}`, type: "tilt", duration: 1.0, roll: side === "right" ? -angle : angle, pose: "tilt" });
      }

      steps.push({ label: "sit", type: "sit", duration: 2.0, pose: "sit" });
      return steps;
    }

    function parsePerformance(text) {
      const speed = readNumber(text, "FORWARD_SPEED_MPS", 0.3);
      const turn = readNumber(text, "TURN_RATE_RPS", 0.2);
      const tilt = readNumber(text, "TILT_ANGLE_DEGREES", 12.0);

      return [
        { label: "sit", type: "sit", duration: 1.0, pose: "sit" },
        { label: "stand_up", type: "stand", duration: 2.0, pose: "stand" },
        { label: "tilt right", type: "tilt", duration: 1.0, roll: tilt, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -tilt, pose: "tilt" },
        { label: "tilt right", type: "tilt", duration: 1.0, roll: tilt, pose: "tilt" },
        { label: "tilt left", type: "tilt", duration: 1.0, roll: -tilt, pose: "tilt" },
        { label: "stretch", type: "stretch", duration: 2.0, pose: "stretch" },
        { label: "walk forward", type: "walk", duration: 4.0, forward: speed, turn: 0.0, pose: "walk" },
        { label: "walk arc", type: "walk", duration: 2.5, forward: speed, turn, pose: "turn" },
        { label: "walk forward", type: "walk", duration: 4.0, forward: speed, turn: 0.0, pose: "walk" },
        { label: "hello", type: "hello", duration: 2.0, pose: "hello" },
        { label: "stop", type: "stop", duration: 0.5, pose: "stop" },
        { label: "sit", type: "sit", duration: 2.0, pose: "sit" }
      ];
    }

    function parseTeleop(text) {
      const forward = readNumber(text, "FORWARD_SPEED_MPS", 0.3);
      const turn = readNumber(text, "TURN_RATE_RPS", 0.3);
      return [
        { label: "stand_up", type: "stand", duration: 2.0, pose: "stand" },
        { label: "W held", type: "walk", duration: 2.0, forward, turn: 0.0, pose: "walk" },
        { label: "A held", type: "walk", duration: 1.2, forward: 0.0, turn, pose: "turn" },
        { label: "D held", type: "walk", duration: 1.2, forward: 0.0, turn: -turn, pose: "turn" },
        { label: "S held", type: "walk", duration: 1.8, forward: -forward, turn: 0.0, pose: "walk" },
        { label: "Space", type: "stop", duration: 0.8, pose: "stop" },
        { label: "Q", type: "sit", duration: 2.0, pose: "sit" }
      ];
    }

    function parseCliRoutines(text) {
      const out = {};
      const names = ["greet", "calm-start", "short-walk", "reset", "turn-left", "turn-right", "back-up-slowly"];

      for (const name of names) {
        const start = text.indexOf(`if name == \"${name}\":`) >= 0
          ? text.indexOf(`if name == \"${name}\":`)
          : text.indexOf(`elif name == \"${name}\":`);
        if (start < 0) {
          continue;
        }
        let end = text.length;
        for (const other of names) {
          if (other === name) {
            continue;
          }
          const probe = text.indexOf(`elif name == \"${other}\":`, start + 1);
          if (probe > start && probe < end) {
            end = probe;
          }
        }
        const elseIndex = text.indexOf("else:", start + 1);
        if (elseIndex > start && elseIndex < end) {
          end = elseIndex;
        }

        const block = text.slice(start, end);
        const steps = parseClientCalls(block);
        if (steps.length) {
          out[`cli.py routine:${name}`] = steps;
        }
      }

      return out;
    }

    async function autoLoadRoutines() {
      const loaders = [
        {
          file: "demo.py",
          parser: (text) => parseClientCalls(text)
        },
        {
          file: "stand_wag_sit_example.py",
          parser: (text) => {
            const steps = [];
            const callRegex = /await\s+send_command\(conn,\s*([A-Z0-9_]+)\)/g;
            let m;
            while ((m = callRegex.exec(text)) !== null) {
              const id = m[1];
              if (id.includes("STAND")) {
                steps.push({ label: "stand_up", type: "stand", duration: 2.0, pose: "stand" });
              } else if (id.includes("HAPPY_WAG")) {
                steps.push({ label: "content", type: "wag", duration: 2.0, pose: "wag" });
              } else if (id.includes("SIT")) {
                steps.push({ label: "sit", type: "sit", duration: 2.0, pose: "sit" });
              }
            }
            return steps;
          }
        },
        { file: "repeat_tilt_sit.py", parser: parseRepeatTilt },
        { file: "square_walk_sit.py", parser: parseSquareWalk },
        { file: "walk_turn_walk_sit.py", parser: parseWalkTurnWalk },
        { file: "performance_routine.py", parser: parsePerformance },
        { file: "pynput_teleop.py", parser: parseTeleop },
        {
          file: "cli.py",
          parser: (text) => parseCliRoutines(text)
        }
      ];

      const loaded = {};
      let loadedCount = 0;

      for (const loader of loaders) {
        try {
          const response = await fetch(`./${loader.file}?t=${Date.now()}`);
          if (!response.ok) {
            continue;
          }
          const text = await response.text();
          const parsed = loader.parser(text);

          if (loader.file === "cli.py") {
            for (const [key, steps] of Object.entries(parsed)) {
              if (Array.isArray(steps) && steps.length > 0) {
                loaded[key] = steps;
                loadedCount += 1;
              }
            }
          } else if (Array.isArray(parsed) && parsed.length > 0) {
            loaded[loader.file] = parsed;
            loadedCount += 1;
          }
        } catch (_err) {
          // Keep fallback static routines when parsing fails.
        }
      }

      if (loadedCount > 0) {
        routines = loaded;
      }

      document.querySelector(".subtitle").textContent =
        loadedCount > 0
          ? `Auto-loaded ${loadedCount} routines from Python files. Refresh after editing to update.`
          : "Using fallback data. Start with a local server and refresh to auto-load Python routines.";
    }

    function setupRoutineList() {
      routineSelect.innerHTML = "";
      for (const name of Object.keys(routines)) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        routineSelect.appendChild(opt);
      }
      if (!routines[sim.routineName]) {
        sim.routineName = Object.keys(routines)[0];
      }
      routineSelect.value = sim.routineName;
    }

    function resetSimulation() {
      sim.steps = routines[sim.routineName] || [];
      sim.stepIndex = 0;
      sim.stepT = 0;
      sim.worldT = 0;
      sim.x = 0;
      sim.y = 0;
      sim.heading = 0;
      sim.rollDeg = 0;
      sim.pose = "idle";
      sim.tailPhase = 0;
      sim.gaitPhase = 0;
      sim.trail = [{ x: 0, y: 0 }];
      sim.complete = false;
      renderTimeline();
      refreshStats();
      draw();
    }

    function worldToCanvas(wx, wy) {
      const cx = canvas.width * 0.5 + wx * PX_PER_M;
      const cy = canvas.height * 0.56 - wy * PX_PER_M;
      return { x: cx, y: cy };
    }

    function update(dt) {
      if (!sim.running || sim.complete) {
        return;
      }

      sim.worldT += dt;

      while (dt > 0 && !sim.complete) {
        const step = sim.steps[sim.stepIndex];
        if (!step) {
          sim.complete = true;
          sim.running = false;
          badge.textContent = "Complete";
          badge.style.background = "#e8f6ef";
          return;
        }

        const remain = step.duration - sim.stepT;
        const used = Math.min(remain, dt);

        applyStep(step, used);

        sim.stepT += used;
        dt -= used;

        if (sim.stepT >= step.duration - 1e-6) {
          sim.stepIndex += 1;
          sim.stepT = 0;
          highlightStep();
        }
      }

      refreshStats();
    }

    function applyStep(step, dt) {
      sim.pose = step.pose || "idle";
      const turn = step.turn || 0;
      const forward = step.forward || 0;

      if (step.type === "walk") {
        sim.heading += turn * dt;
        sim.x += Math.cos(sim.heading) * forward * dt;
        sim.y += Math.sin(sim.heading) * forward * dt;
        sim.gaitPhase += dt * Math.max(1.8, Math.abs(forward) * 7.5 + Math.abs(turn) * 4.0);

        const last = sim.trail[sim.trail.length - 1];
        if (!last || Math.hypot(sim.x - last.x, sim.y - last.y) > 0.02) {
          sim.trail.push({ x: sim.x, y: sim.y });
        }
      }

      if (step.type === "tilt") {
        sim.rollDeg = step.roll || 0;
      } else if (Math.abs(sim.rollDeg) > 0.001) {
        sim.rollDeg *= Math.max(0, 1 - dt * 2.3);
      }

      if (step.type === "wag" || step.type === "hello") {
        sim.tailPhase += dt * 10;
      } else {
        sim.tailPhase += dt * 2;
      }
    }

    function drawGrid() {
      const spacing = PX_PER_M;
      ctx.save();
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--grid");
      ctx.lineWidth = 1;

      for (let x = canvas.width * 0.5 % spacing; x < canvas.width; x += spacing) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }

      for (let y = canvas.height * 0.56 % spacing; y < canvas.height; y += spacing) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      ctx.restore();
    }

    function drawTrail() {
      if (sim.trail.length < 2) {
        return;
      }
      ctx.save();
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--trail");
      ctx.lineWidth = 3;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      ctx.beginPath();
      const p0 = worldToCanvas(sim.trail[0].x, sim.trail[0].y);
      ctx.moveTo(p0.x, p0.y);
      for (let i = 1; i < sim.trail.length; i += 1) {
        const p = worldToCanvas(sim.trail[i].x, sim.trail[i].y);
        ctx.lineTo(p.x, p.y);
      }
      ctx.stroke();
      ctx.restore();
    }

    function drawDog() {
      const c = worldToCanvas(sim.x, sim.y);
      ctx.save();
      ctx.translate(c.x, c.y);
      ctx.rotate(sim.heading + (sim.rollDeg * Math.PI / 180) * 0.35);

      const bodyW = 78;
      const bodyH = sim.pose === "sit" ? 28 : 34;
      const headX = bodyW * 0.52;

      const legLift = Math.sin(sim.gaitPhase * 8) * 4;
      const isWalking = sim.pose === "walk" || sim.pose === "turn";

      // legs
      ctx.strokeStyle = "#2f3f4d";
      ctx.lineWidth = 6;
      const legY = bodyH * 0.47;
      const frontLift = isWalking ? legLift : 0;
      const rearLift = isWalking ? -legLift : 0;
      drawLeg(-22, legY, rearLift);
      drawLeg(-7, legY, -rearLift);
      drawLeg(7, legY, frontLift);
      drawLeg(22, legY, -frontLift);

      // body
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--dog");
      roundedRect(-bodyW * 0.5, -bodyH * 0.5, bodyW, bodyH, 12);
      ctx.fill();

      // head
      ctx.beginPath();
      ctx.fillStyle = "#243645";
      ctx.moveTo(headX, -12);
      ctx.lineTo(headX + 24, 0);
      ctx.lineTo(headX, 12);
      ctx.closePath();
      ctx.fill();

      // ear accent
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--dog-detail");
      ctx.beginPath();
      ctx.arc(headX + 8, -8, 4, 0, TAU);
      ctx.fill();

      // tail
      const wagAmp = sim.pose === "wag" ? 0.8 : sim.pose === "hello" ? 0.55 : 0.2;
      const tailAngle = Math.sin(sim.tailPhase * 8) * wagAmp - Math.PI;
      ctx.strokeStyle = "#243645";
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.moveTo(-bodyW * 0.5, -4);
      ctx.lineTo(-bodyW * 0.5 + Math.cos(tailAngle) * 22, -4 + Math.sin(tailAngle) * 22);
      ctx.stroke();

      // eye
      ctx.fillStyle = "#f5f0e8";
      ctx.beginPath();
      ctx.arc(headX + 11, -2, 2.2, 0, TAU);
      ctx.fill();

      if (sim.pose === "stretch") {
        ctx.strokeStyle = "#1f2933";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(-18, -26);
        ctx.lineTo(20, -30);
        ctx.stroke();
      }

      if (sim.pose === "balance") {
        ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--ok");
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(0, 0, 34, 0, TAU);
        ctx.stroke();
      }

      ctx.restore();

      function drawLeg(x, y, lift) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, y + 24 + lift);
        ctx.stroke();
      }

      function roundedRect(x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.arcTo(x + w, y, x + w, y + h, r);
        ctx.arcTo(x + w, y + h, x, y + h, r);
        ctx.arcTo(x, y + h, x, y, r);
        ctx.arcTo(x, y, x + w, y, r);
        ctx.closePath();
      }
    }

    function drawCompass() {
      ctx.save();
      ctx.translate(88, 84);
      ctx.fillStyle = "rgba(255,255,255,0.7)";
      ctx.strokeStyle = "#22323d";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, 36, 0, TAU);
      ctx.fill();
      ctx.stroke();

      ctx.rotate(sim.heading);
      ctx.strokeStyle = "#e76f51";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(24, 0);
      ctx.stroke();
      ctx.restore();
    }

    function drawStepLabel() {
      const step = sim.steps[sim.stepIndex] || null;
      ctx.save();
      ctx.fillStyle = "rgba(18, 35, 40, 0.88)";
      if (typeof ctx.roundRect === "function") {
        ctx.roundRect(18, canvas.height - 58, canvas.width - 36, 38, 8);
      } else {
        ctx.rect(18, canvas.height - 58, canvas.width - 36, 38);
      }
      ctx.fill();
      ctx.fillStyle = "#f8f4eb";
      ctx.font = "600 16px 'Avenir Next', 'Trebuchet MS', sans-serif";
      ctx.fillText(step ? `Step ${sim.stepIndex + 1}: ${step.label}` : "Routine complete", 32, canvas.height - 33);
      ctx.restore();
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawGrid();
      drawTrail();
      drawDog();
      drawCompass();
      drawStepLabel();
    }

    function renderTimeline() {
      timeline.innerHTML = "";
      sim.steps.forEach((step, i) => {
        const row = document.createElement("div");
        row.className = "step" + (i === sim.stepIndex ? " active" : "");
        row.textContent = `${i + 1}. ${step.label} (${step.duration.toFixed(1)}s)`;
        timeline.appendChild(row);
      });
    }

    function highlightStep() {
      const rows = timeline.querySelectorAll(".step");
      rows.forEach((r, idx) => {
        r.classList.toggle("active", idx === sim.stepIndex);
      });
    }

    function refreshStats() {
      const step = sim.steps[sim.stepIndex] || null;
      statStep.textContent = step ? `${sim.stepIndex + 1}/${sim.steps.length}` : `${sim.steps.length}/${sim.steps.length}`;
      statPose.textContent = sim.pose || "idle";
      statPos.textContent = `${sim.x.toFixed(2)}, ${sim.y.toFixed(2)}`;
      statHeading.textContent = `${(sim.heading * 180 / Math.PI).toFixed(0)}°`;
      routineLabel.textContent = sim.routineName;

      if (sim.running) {
        badge.textContent = "Running";
        badge.style.background = "#e8f6ef";
      } else if (sim.complete) {
        badge.textContent = "Complete";
        badge.style.background = "#fff0e5";
      } else {
        badge.textContent = "Paused";
        badge.style.background = "#fff";
      }
    }

    let lastTime = performance.now();
    function frame(now) {
      const dt = Math.min((now - lastTime) / 1000, 0.05) * sim.speed;
      lastTime = now;
      update(dt);
      draw();
      requestAnimationFrame(frame);
    }

    routineSelect.addEventListener("change", (e) => {
      sim.routineName = e.target.value;
      resetSimulation();
    });

    speedSlider.addEventListener("input", (e) => {
      sim.speed = Number(e.target.value);
    });

    playBtn.addEventListener("click", () => {
      sim.running = true;
      refreshStats();
    });

    pauseBtn.addEventListener("click", () => {
      sim.running = false;
      refreshStats();
    });

    resetBtn.addEventListener("click", () => {
      sim.running = false;
      resetSimulation();
    });

    async function init() {
      await autoLoadRoutines();
      setupRoutineList();
      resetSimulation();
      refreshStats();
      requestAnimationFrame(frame);
    }

    init();
