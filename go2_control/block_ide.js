// Go2 Block IDE — Blockly block definitions, Python code generation, and page wiring.
//
// Blocks are grouped to mirror go2_control's modules: movement (client.py),
// camera/LIDAR (camera_view.py / lidar_view.py), telemetry (telemetry.py),
// and LED/audio/safety (experimental.py / audio.py). Each block's generator
// emits the exact call signature used in those files.

(function () {
  "use strict";

  // Blockly 10/11 moved generators out of the `Blockly` namespace into their
  // own globals (`python.pythonGenerator`) with a `.forBlock` dict. Older
  // builds still expose `Blockly.Python` directly. Support both so this page
  // keeps working if the CDN resolves a different Blockly version.
  const pyGenerator =
    (typeof python !== "undefined" && python.pythonGenerator) ||
    (typeof Blockly !== "undefined" && Blockly.Python);

  function defineGenerator(blockType, fn) {
    if (pyGenerator.forBlock) {
      pyGenerator.forBlock[blockType] = fn;
    } else {
      pyGenerator[blockType] = fn;
    }
  }

  function generateCodeForWorkspace(workspace) {
    if (pyGenerator.workspaceToCode) {
      return pyGenerator.workspaceToCode(workspace);
    }
    return Blockly.Python.workspaceToCode(workspace);
  }

  // ---------------------------------------------------------------------
  // Block definitions
  // ---------------------------------------------------------------------

  const HUE = {
    movement: 210,
    gait: 30,
    gestures: 290,
    camera: 55,
    telemetry: 175,
    safety: 330,
    control: 0,
  };

  const boolField = (name, def) => ({
    type: "field_dropdown",
    name,
    options: [
      ["enable", "True"],
      ["disable", "False"],
    ],
  });

  Blockly.defineBlocksWithJsonArray([
    // --- Movement -------------------------------------------------------
    { type: "go2_balance_stand", message0: "balance stand", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.balance_stand()" },
    { type: "go2_stand_up", message0: "stand up", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.stand_up()" },
    { type: "go2_stand_down", message0: "stand down", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.stand_down()" },
    { type: "go2_recovery_stand", message0: "recovery stand", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.recovery_stand()" },
    { type: "go2_sit", message0: "sit", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.sit()" },
    { type: "go2_rise_sit", message0: "rise from sit", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.rise_sit()" },
    { type: "go2_stop_move", message0: "stop moving", previousStatement: null, nextStatement: null, colour: HUE.movement, tooltip: "client.stop_move()" },
    {
      type: "go2_walk_for",
      message0: "walk forward %1 m/s sideways %2 m/s turn %3 rps for %4 s",
      args0: [
        { type: "field_number", name: "FORWARD", value: 0.1, min: -0.3, max: 0.3, precision: 0.01 },
        { type: "field_number", name: "SIDEWAYS", value: 0, min: -0.3, max: 0.3, precision: 0.01 },
        { type: "field_number", name: "TURN", value: 0, min: -1, max: 1, precision: 0.05 },
        { type: "field_number", name: "DURATION", value: 2, min: 0.1, max: 30, precision: 0.1 },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.movement,
      tooltip: "client.walk_for(forward, duration_s=duration, sideways_mps=sideways, turn_rps=turn) -- capped at 0.3 m/s / 1.0 rps",
    },
    {
      type: "go2_move_once",
      message0: "send one move: forward %1 m/s sideways %2 m/s turn %3 rps",
      args0: [
        { type: "field_number", name: "FORWARD", value: 0.1, min: -0.3, max: 0.3, precision: 0.01 },
        { type: "field_number", name: "SIDEWAYS", value: 0, min: -0.3, max: 0.3, precision: 0.01 },
        { type: "field_number", name: "TURN", value: 0, min: -1, max: 1, precision: 0.05 },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.movement,
      tooltip: "client.move(...) -- a single command; the robot expects these repeated to keep moving, use 'walk forward...for' instead unless you're building your own loop",
    },
    {
      type: "go2_speed_level",
      message0: "set speed level %1",
      args0: [{ type: "field_dropdown", name: "LEVEL", options: [["0 - slow", "0"], ["1 - medium", "1"], ["2 - fast", "2"]] }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.movement,
      tooltip: "client.speed_level(level)",
    },

    // --- Gait & posture ---------------------------------------------------
    {
      type: "go2_switch_gait",
      message0: "switch gait to id %1",
      args0: [{ type: "field_number", name: "GAIT", value: 0, min: 0, max: 10, precision: 1 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.gait,
      tooltip: "client.switch_gait(gait_id) -- valid IDs are firmware-dependent",
    },
    {
      type: "go2_set_body_height",
      message0: "set body height offset %1 m",
      args0: [{ type: "field_number", name: "HEIGHT", value: 0, min: -0.1, max: 0.1, precision: 0.01 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.gait,
      tooltip: "client.set_body_height(height_m)",
    },
    {
      type: "go2_set_foot_raise_height",
      message0: "set foot raise height offset %1 m",
      args0: [{ type: "field_number", name: "HEIGHT", value: 0, min: -0.1, max: 0.1, precision: 0.01 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.gait,
      tooltip: "client.set_foot_raise_height(height_m)",
    },
    {
      type: "go2_pose",
      message0: "%1 manual pose mode",
      args0: [{ type: "field_dropdown", name: "ENABLE", options: [["enable", "True"], ["disable", "False"]] }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.gait,
      tooltip: "client.pose(enable)",
    },
    {
      type: "go2_euler_tilt",
      message0: "tilt body roll %1 pitch %2 yaw %3 (radians)",
      args0: [
        { type: "field_number", name: "ROLL", value: 0, min: -0.5, max: 0.5, precision: 0.05 },
        { type: "field_number", name: "PITCH", value: 0, min: -0.5, max: 0.5, precision: 0.05 },
        { type: "field_number", name: "YAW", value: 0, min: -0.5, max: 0.5, precision: 0.05 },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.gait,
      tooltip: "client.euler_body_tilt(roll, pitch, yaw)",
    },

    // --- Gestures ---------------------------------------------------------
    { type: "go2_hello", message0: "wave hello", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.hello()" },
    { type: "go2_content", message0: "content (happy)", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.content()" },
    { type: "go2_stretch", message0: "stretch", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.stretch()" },
    { type: "go2_heart_pose", message0: "heart pose", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.heart_pose()" },
    { type: "go2_dance1", message0: "dance routine 1", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.dance1()" },
    { type: "go2_dance2", message0: "dance routine 2", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.dance2()" },
    { type: "go2_wallow", message0: "wallow", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.wallow()" },
    { type: "go2_scrape", message0: "scrape", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.scrape()" },
    { type: "go2_wiggle_hips", message0: "wiggle hips", previousStatement: null, nextStatement: null, colour: HUE.gestures, tooltip: "client.wiggle_hips()" },

    // --- Camera & LIDAR -----------------------------------------------------
    {
      type: "go2_camera_snapshots",
      message0: "save %1 camera snapshot(s) every %2 s to folder %3",
      args0: [
        { type: "field_number", name: "COUNT", value: 5, min: 1, max: 50, precision: 1 },
        { type: "field_number", name: "INTERVAL", value: 1, min: 0.1, max: 10, precision: 0.1 },
        { type: "field_input", name: "OUTDIR", text: "camera_snapshots" },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.camera,
      tooltip: "capture_snapshots(client.conn, Path(out_dir), count, interval_s)",
    },
    {
      type: "go2_lidar_capture",
      message0: "capture %1 LIDAR message(s) %2 to folder %3",
      args0: [
        { type: "field_number", name: "COUNT", value: 20, min: 1, max: 200, precision: 1 },
        { type: "field_dropdown", name: "RECORD", options: [["and record", "True"], ["(view only)", "False"]] },
        { type: "field_input", name: "OUTDIR", text: "lidar_recording" },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.camera,
      tooltip: "stream_lidar(client.conn, count, out_dir=...) -- folder is ignored if 'view only' is selected",
    },

    // --- Telemetry ----------------------------------------------------------
    {
      type: "go2_print_state",
      message0: "print %1 telemetry message(s) (battery / orientation / velocity)",
      args0: [{ type: "field_number", name: "COUNT", value: 5, min: 1, max: 100, precision: 1 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.telemetry,
      tooltip: "stream_state(client.conn, count) -- read-only",
    },
    {
      type: "go2_log_odometry",
      message0: "log %1 odometry message(s) to %2",
      args0: [
        { type: "field_number", name: "COUNT", value: 20, min: 1, max: 200, precision: 1 },
        { type: "field_input", name: "OUTCSV", text: "odometry_log.csv" },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.telemetry,
      tooltip: "log_odometry(client.conn, count, out_csv) -- read-only",
    },

    // --- LED / audio / safety -----------------------------------------------
    {
      type: "go2_set_led_color",
      message0: "set LED color %1 for %2 s",
      args0: [
        {
          type: "field_dropdown",
          name: "COLOR",
          options: [["white", "white"], ["red", "red"], ["yellow", "yellow"], ["blue", "blue"], ["green", "green"], ["cyan", "cyan"], ["purple", "purple"]],
        },
        { type: "field_number", name: "TIME", value: 5, min: 1, max: 30, precision: 1 },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.safety,
      tooltip: "set_led_color(client.conn, color, time_s=time)",
    },
    {
      type: "go2_set_volume",
      message0: "set speaker volume to %1 (0-10)",
      args0: [{ type: "field_number", name: "VOLUME", value: 5, min: 0, max: 10, precision: 1 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.safety,
      tooltip: "set_volume(client.conn, volume)",
    },
    {
      type: "go2_set_brightness",
      message0: "set status light brightness to %1 (0-10)",
      args0: [{ type: "field_number", name: "BRIGHTNESS", value: 5, min: 0, max: 10, precision: 1 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.safety,
      tooltip: "set_brightness(client.conn, brightness)",
    },
    {
      type: "go2_set_obstacle_avoidance",
      message0: "%1 obstacle avoidance",
      args0: [{ type: "field_dropdown", name: "ENABLED", options: [["enable", "True"], ["disable", "False"]] }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.safety,
      tooltip: "set_obstacle_avoidance(client.conn, enabled)",
    },
    {
      type: "go2_play_audio",
      message0: "play sound id %1",
      args0: [{ type: "field_input", name: "AUDIO_ID", text: "1" }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.safety,
      tooltip: "play_audio(client.conn, audio_id) -- run 'list available sounds' first to find valid ids",
    },
    {
      type: "go2_list_audio",
      message0: "print available sounds",
      previousStatement: null,
      nextStatement: null,
      colour: HUE.safety,
      tooltip: "print(await get_audio_list(client.conn))",
    },

    // --- Control ------------------------------------------------------------
    {
      type: "go2_wait",
      message0: "wait %1 s",
      args0: [{ type: "field_number", name: "SECONDS", value: 1, min: 0.1, max: 30, precision: 0.1 }],
      previousStatement: null,
      nextStatement: null,
      colour: HUE.control,
      tooltip: "asyncio.sleep(seconds)",
    },
  ]);

  // ---------------------------------------------------------------------
  // Python generators
  // ---------------------------------------------------------------------

  const simple = (call) => () => call + "\n";
  defineGenerator("go2_balance_stand", simple("await client.balance_stand()"));
  defineGenerator("go2_stand_up", simple("await client.stand_up()"));
  defineGenerator("go2_stand_down", simple("await client.stand_down()"));
  defineGenerator("go2_recovery_stand", simple("await client.recovery_stand()"));
  defineGenerator("go2_sit", simple("await client.sit()"));
  defineGenerator("go2_rise_sit", simple("await client.rise_sit()"));
  defineGenerator("go2_stop_move", simple("await client.stop_move()"));
  defineGenerator("go2_hello", simple("await client.hello()"));
  defineGenerator("go2_content", simple("await client.content()"));
  defineGenerator("go2_stretch", simple("await client.stretch()"));
  defineGenerator("go2_heart_pose", simple("await client.heart_pose()"));
  defineGenerator("go2_dance1", simple("await client.dance1()"));
  defineGenerator("go2_dance2", simple("await client.dance2()"));
  defineGenerator("go2_wallow", simple("await client.wallow()"));
  defineGenerator("go2_scrape", simple("await client.scrape()"));
  defineGenerator("go2_wiggle_hips", simple("await client.wiggle_hips()"));
  defineGenerator("go2_list_audio", simple("print(await get_audio_list(client.conn))"));

  defineGenerator("go2_walk_for", (block) => {
    const forward = block.getFieldValue("FORWARD");
    const sideways = block.getFieldValue("SIDEWAYS");
    const turn = block.getFieldValue("TURN");
    const duration = block.getFieldValue("DURATION");
    return `await client.walk_for(${forward}, duration_s=${duration}, sideways_mps=${sideways}, turn_rps=${turn})\n`;
  });

  defineGenerator("go2_move_once", (block) => {
    const forward = block.getFieldValue("FORWARD");
    const sideways = block.getFieldValue("SIDEWAYS");
    const turn = block.getFieldValue("TURN");
    return `await client.move(${forward}, sideways_mps=${sideways}, turn_rps=${turn})\n`;
  });

  defineGenerator("go2_speed_level", (block) => `await client.speed_level(${block.getFieldValue("LEVEL")})\n`);
  defineGenerator("go2_switch_gait", (block) => `await client.switch_gait(${block.getFieldValue("GAIT")})\n`);
  defineGenerator("go2_set_body_height", (block) => `await client.set_body_height(${block.getFieldValue("HEIGHT")})\n`);
  defineGenerator("go2_set_foot_raise_height", (block) => `await client.set_foot_raise_height(${block.getFieldValue("HEIGHT")})\n`);
  defineGenerator("go2_pose", (block) => `await client.pose(${block.getFieldValue("ENABLE")})\n`);
  defineGenerator("go2_euler_tilt", (block) => {
    const roll = block.getFieldValue("ROLL");
    const pitch = block.getFieldValue("PITCH");
    const yaw = block.getFieldValue("YAW");
    return `await client.euler_body_tilt(${roll}, ${pitch}, ${yaw})\n`;
  });

  const pyStr = (s) => JSON.stringify(String(s));

  defineGenerator("go2_camera_snapshots", (block) => {
    const count = block.getFieldValue("COUNT");
    const interval = block.getFieldValue("INTERVAL");
    const outdir = pyStr(block.getFieldValue("OUTDIR"));
    return `await capture_snapshots(client.conn, Path(${outdir}), ${count}, ${interval})\n`;
  });

  defineGenerator("go2_lidar_capture", (block) => {
    const count = block.getFieldValue("COUNT");
    const record = block.getFieldValue("RECORD");
    const outdir = pyStr(block.getFieldValue("OUTDIR"));
    const outArg = record === "True" ? `, out_dir=Path(${outdir})` : "";
    return `await stream_lidar(client.conn, ${count}${outArg})\n`;
  });

  defineGenerator("go2_print_state", (block) => `await stream_state(client.conn, ${block.getFieldValue("COUNT")})\n`);
  defineGenerator("go2_log_odometry", (block) => {
    const count = block.getFieldValue("COUNT");
    const outcsv = pyStr(block.getFieldValue("OUTCSV"));
    return `await log_odometry(client.conn, ${count}, Path(${outcsv}))\n`;
  });

  defineGenerator("go2_set_led_color", (block) => {
    const color = pyStr(block.getFieldValue("COLOR"));
    const time = block.getFieldValue("TIME");
    return `await set_led_color(client.conn, ${color}, time_s=${time})\n`;
  });
  defineGenerator("go2_set_volume", (block) => `await set_volume(client.conn, ${block.getFieldValue("VOLUME")})\n`);
  defineGenerator("go2_set_brightness", (block) => `await set_brightness(client.conn, ${block.getFieldValue("BRIGHTNESS")})\n`);
  defineGenerator("go2_set_obstacle_avoidance", (block) => `await set_obstacle_avoidance(client.conn, ${block.getFieldValue("ENABLED")})\n`);
  defineGenerator("go2_play_audio", (block) => `await play_audio(client.conn, ${pyStr(block.getFieldValue("AUDIO_ID"))})\n`);
  defineGenerator("go2_wait", (block) => `await asyncio.sleep(${block.getFieldValue("SECONDS")})\n`);

  // ---------------------------------------------------------------------
  // Toolbox
  // ---------------------------------------------------------------------

  const toolboxXml = `
    <xml>
      <category name="Movement" colour="${HUE.movement}">
        <block type="go2_balance_stand"></block>
        <block type="go2_stand_up"></block>
        <block type="go2_stand_down"></block>
        <block type="go2_recovery_stand"></block>
        <block type="go2_sit"></block>
        <block type="go2_rise_sit"></block>
        <block type="go2_stop_move"></block>
        <block type="go2_walk_for"></block>
        <block type="go2_move_once"></block>
        <block type="go2_speed_level"></block>
      </category>
      <category name="Gait &amp; Posture" colour="${HUE.gait}">
        <block type="go2_switch_gait"></block>
        <block type="go2_set_body_height"></block>
        <block type="go2_set_foot_raise_height"></block>
        <block type="go2_pose"></block>
        <block type="go2_euler_tilt"></block>
      </category>
      <category name="Gestures" colour="${HUE.gestures}">
        <block type="go2_hello"></block>
        <block type="go2_content"></block>
        <block type="go2_stretch"></block>
        <block type="go2_heart_pose"></block>
        <block type="go2_dance1"></block>
        <block type="go2_dance2"></block>
        <block type="go2_wallow"></block>
        <block type="go2_scrape"></block>
        <block type="go2_wiggle_hips"></block>
      </category>
      <category name="Camera &amp; LIDAR" colour="${HUE.camera}">
        <block type="go2_camera_snapshots"></block>
        <block type="go2_lidar_capture"></block>
      </category>
      <category name="Telemetry" colour="${HUE.telemetry}">
        <block type="go2_print_state"></block>
        <block type="go2_log_odometry"></block>
      </category>
      <category name="LED / Audio / Safety" colour="${HUE.safety}">
        <block type="go2_set_led_color"></block>
        <block type="go2_set_volume"></block>
        <block type="go2_set_brightness"></block>
        <block type="go2_set_obstacle_avoidance"></block>
        <block type="go2_play_audio"></block>
        <block type="go2_list_audio"></block>
      </category>
      <category name="Control" colour="${HUE.control}">
        <block type="go2_wait"></block>
        <block type="controls_repeat_ext">
          <value name="TIMES">
            <shadow type="math_number">
              <field name="NUM">3</field>
            </shadow>
          </value>
        </block>
      </category>
    </xml>
  `;

  // ---------------------------------------------------------------------
  // Workspace + code panel wiring
  // ---------------------------------------------------------------------

  const workspace = Blockly.inject("blocklyDiv", {
    toolbox: toolboxXml,
    grid: { spacing: 22, length: 3, colour: "#e1d9ca", snap: true },
    zoom: { controls: true, wheel: true, startScale: 0.9 },
    trashcan: true,
  });

  // Detects which optional helper functions the generated body actually
  // calls, so the saved file only imports what it uses.
  function buildImports(body) {
    const lines = ["import asyncio", "from go2_control.client import Go2ControlClient"];
    if (body.includes("Path(")) lines.splice(1, 0, "from pathlib import Path");
    if (body.includes("capture_snapshots(")) lines.push("from go2_control.camera_view import capture_snapshots");
    if (body.includes("stream_lidar(")) lines.push("from go2_control.lidar_view import stream_lidar");
    if (body.includes("stream_state(") || body.includes("log_odometry(")) {
      lines.push("from go2_control.telemetry import stream_state, log_odometry");
    }
    if (body.includes("get_audio_list(") || body.includes("play_audio(")) {
      lines.push("from go2_control.audio import get_audio_list, play_audio");
    }
    if (
      body.includes("set_led_color(") ||
      body.includes("set_volume(") ||
      body.includes("set_brightness(") ||
      body.includes("set_obstacle_avoidance(")
    ) {
      lines.push("from go2_control.experimental import set_led_color, set_volume, set_brightness, set_obstacle_avoidance");
    }
    return lines;
  }

  function indent(text, spaces) {
    const pad = " ".repeat(spaces);
    return text
      .split("\n")
      .map((line) => (line.trim() ? pad + line : line))
      .join("\n");
  }

  function generateFullScript() {
    const rawBody = generateCodeForWorkspace(workspace) || "";
    const body = rawBody.trim() ? rawBody : "pass\n";
    const imports = buildImports(body);
    const indentedBody = indent(body.trimEnd(), 8);

    return [
      '"""Generated by the Go2 Block IDE. Review before running on hardware."""',
      "",
      imports.join("\n"),
      "",
      "",
      "async def main() -> None:",
      "    client = Go2ControlClient()",
      "    await client.connect()",
      "    try:",
      indentedBody,
      "    finally:",
      "        await client.stop_move()",
      "        await client.disconnect()",
      "",
      "",
      'if __name__ == "__main__":',
      "    asyncio.run(main())",
      "",
    ].join("\n");
  }

  const codeOutput = document.getElementById("codeOutput");
  const statusMsg = document.getElementById("statusMsg");

  function refreshCode() {
    codeOutput.textContent = generateFullScript();
  }

  workspace.addChangeListener((event) => {
    if (event.isUiEvent) return;
    refreshCode();
  });

  document.getElementById("saveBtn").addEventListener("click", () => {
    const blob = new Blob([codeOutput.textContent], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "go2_program.py";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    statusMsg.textContent = "Saved go2_program.py";
  });

  document.getElementById("copyBtn").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(codeOutput.textContent);
      statusMsg.textContent = "Copied to clipboard";
    } catch (err) {
      statusMsg.textContent = "Copy failed — select and copy manually";
    }
  });

  document.getElementById("clearBtn").addEventListener("click", () => {
    if (confirm("Clear all blocks from the workspace?")) {
      workspace.clear();
      refreshCode();
      statusMsg.textContent = "Workspace cleared";
    }
  });

  // Seed a small starter stack so the page isn't empty on first load.
  const starterXml = Blockly.utils.xml.textToDom(`
    <xml>
      <block type="go2_balance_stand" x="30" y="30">
        <next>
          <block type="go2_wait"><field name="SECONDS">1</field>
            <next>
              <block type="go2_stand_up">
                <next>
                  <block type="go2_hello"></block>
                </next>
              </block>
            </next>
          </block>
        </next>
      </block>
    </xml>
  `);
  Blockly.Xml.domToWorkspace(starterXml, workspace);
  refreshCode();
})();
