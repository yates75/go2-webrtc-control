const statusEl = document.getElementById("status");
const controlStateEl = document.getElementById("controlState");
const videoStateEl = document.getElementById("videoState");
const twistEl = document.getElementById("twist");
const videoEl = document.getElementById("robotVideo");

const btnConnect = document.getElementById("btnConnect");
const btnDisconnect = document.getElementById("btnDisconnect");
const btnVideo = document.getElementById("btnVideo");
const btnVR = document.getElementById("btnVR");

const MAX_FORWARD = 0.3;
const MAX_TURN = 0.7;
const SEND_HZ = 12;

let ws = null;
let pc = null;
let sendTimer = null;
let gamepadTimer = null;

const twist = { vx: 0.0, wz: 0.0 };

function setStatus(text) {
  statusEl.textContent = text;
}

function setControlState(text) {
  controlStateEl.textContent = text;
}

function setVideoState(text) {
  videoStateEl.textContent = text;
}

function updateTwistUI() {
  twistEl.textContent = `vx=${twist.vx.toFixed(2)}, wz=${twist.wz.toFixed(2)}`;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function wsUrl() {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${window.location.host}/ws/control`;
}

async function connectControl() {
  if (ws && ws.readyState <= 1) {
    return;
  }

  ws = new WebSocket(wsUrl());

  ws.addEventListener("open", () => {
    setControlState("connected");
    setStatus("control connected");
    startControlLoop();
  });

  ws.addEventListener("close", () => {
    setControlState("disconnected");
    setStatus("control closed");
    stopControlLoop();
  });

  ws.addEventListener("error", () => {
    setStatus("control error");
  });
}

function disconnectControl() {
  stopControlLoop();
  if (ws) {
    ws.close();
    ws = null;
  }
  setControlState("disconnected");
}

function sendJson(payload) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }
  ws.send(JSON.stringify(payload));
}

function startControlLoop() {
  stopControlLoop();
  const intervalMs = Math.round(1000 / SEND_HZ);

  sendTimer = window.setInterval(() => {
    sendJson({ type: "heartbeat", stamp_ms: Date.now() });
    sendJson({ type: "twist", vx: twist.vx, wz: twist.wz, stamp_ms: Date.now() });
  }, intervalMs);

  gamepadTimer = window.setInterval(pollGamepads, intervalMs);
}

function stopControlLoop() {
  if (sendTimer !== null) {
    clearInterval(sendTimer);
    sendTimer = null;
  }
  if (gamepadTimer !== null) {
    clearInterval(gamepadTimer);
    gamepadTimer = null;
  }
}

function sendAction(name) {
  sendJson({ type: "action", name, stamp_ms: Date.now() });
  setStatus(`action: ${name}`);
}

function pollGamepads() {
  const pads = navigator.getGamepads ? navigator.getGamepads() : [];
  const gp = pads && pads[0] ? pads[0] : null;
  if (!gp) {
    return;
  }

  // Common mapping: left stick Y (index 1), right stick X (index 2).
  const ly = gp.axes[1] || 0;
  const rx = gp.axes[2] || 0;

  twist.vx = clamp(-ly * MAX_FORWARD, -MAX_FORWARD, MAX_FORWARD);
  twist.wz = clamp(rx * MAX_TURN, -MAX_TURN, MAX_TURN);
  updateTwistUI();
}

async function connectVideo() {
  if (pc) {
    return;
  }

  pc = new RTCPeerConnection();
  pc.addTransceiver("video", { direction: "recvonly" });

  pc.ontrack = (event) => {
    const [stream] = event.streams;
    if (stream) {
      videoEl.srcObject = stream;
      setVideoState("connected");
      setStatus("video connected");
    }
  };

  pc.onconnectionstatechange = () => {
    if (pc.connectionState === "failed" || pc.connectionState === "disconnected") {
      setVideoState(pc.connectionState);
    }
  };

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const response = await fetch("/api/webrtc/offer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sdp: offer.sdp, type: offer.type }),
  });

  if (!response.ok) {
    setStatus("video offer failed");
    return;
  }

  const answer = await response.json();
  await pc.setRemoteDescription(answer);
}

async function enterVR() {
  if (!navigator.xr) {
    setStatus("WebXR not available in this browser");
    return;
  }

  try {
    const supported = await navigator.xr.isSessionSupported("immersive-vr");
    if (!supported) {
      setStatus("immersive-vr not supported on this device/browser");
      return;
    }

    // Requesting session is enough to switch to headset immersive mode.
    const session = await navigator.xr.requestSession("immersive-vr");
    session.addEventListener("end", () => setStatus("VR session ended"));
    setStatus("VR session started");
  } catch (err) {
    setStatus(`VR error: ${String(err)}`);
  }
}

function bindKeyboardFallback() {
  // Keyboard fallback for quick desktop testing.
  window.addEventListener("keydown", (event) => {
    if (event.repeat) {
      return;
    }
    if (event.key === "w") {
      twist.vx = MAX_FORWARD;
    } else if (event.key === "s") {
      twist.vx = -MAX_FORWARD;
    } else if (event.key === "a") {
      twist.wz = MAX_TURN;
    } else if (event.key === "d") {
      twist.wz = -MAX_TURN;
    } else if (event.key === " ") {
      twist.vx = 0;
      twist.wz = 0;
      sendAction("stop");
    }
    updateTwistUI();
  });

  window.addEventListener("keyup", (event) => {
    if (event.key === "w" || event.key === "s") {
      twist.vx = 0;
    }
    if (event.key === "a" || event.key === "d") {
      twist.wz = 0;
    }
    updateTwistUI();
  });
}

btnConnect.addEventListener("click", connectControl);
btnDisconnect.addEventListener("click", disconnectControl);
btnVideo.addEventListener("click", connectVideo);
btnVR.addEventListener("click", enterVR);

document.querySelectorAll("button[data-action]").forEach((button) => {
  button.addEventListener("click", () => sendAction(button.dataset.action));
});

bindKeyboardFallback();
updateTwistUI();
setStatus("ready");
setControlState("disconnected");
setVideoState("disconnected");
