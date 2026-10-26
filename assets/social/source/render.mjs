import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const port = 9333;
const html = resolve(root, "posts.html");

const jobs = [
  ["price-portrait", "../price-1080x1350.png", 1080, 1350],
  ["price-square", "../price-1080x1080.png", 1080, 1080],
  ["speed-portrait", "../speed-1080x1350.png", 1080, 1350],
  ["speed-square", "../speed-1080x1080.png", 1080, 1080],
  ["included-portrait", "../included-1080x1350.png", 1080, 1350],
  ["included-square", "../included-1080x1080.png", 1080, 1080],
  ["before-after-portrait", "../before-after-1080x1350.png", 1080, 1350],
  ["before-after-square", "../before-after-1080x1080.png", 1080, 1080],
  ["faq-portrait", "../faq-1080x1350.png", 1080, 1350],
  ["faq-square", "../faq-1080x1080.png", 1080, 1080],
  ["how-portrait", "../how-1080x1350.png", 1080, 1350],
  ["how-square", "../how-1080x1080.png", 1080, 1080],
  ["carousel-01", "../carousel/01-offer-1080x1350.png", 1080, 1350],
  ["carousel-02", "../carousel/02-included-1080x1350.png", 1080, 1350],
  ["carousel-03", "../carousel/03-how-1080x1350.png", 1080, 1350],
  ["carousel-04", "../carousel/04-before-after-1080x1350.png", 1080, 1350],
  ["carousel-05", "../carousel/05-quote-1080x1350.png", 1080, 1350],
];

const chrome = spawn("google-chrome", [
  "--headless=new",
  "--no-sandbox",
  "--disable-gpu",
  "--disable-dev-shm-usage",
  "--hide-scrollbars",
  "--force-device-scale-factor=1",
  `--remote-debugging-port=${port}`,
  "--user-data-dir=/tmp/newco-social-chrome",
  "about:blank",
], { stdio: "ignore" });

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function waitForChrome() {
  for (let i = 0; i < 50; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) return;
    } catch {}
    await sleep(100);
  }
  throw new Error("Chrome did not start");
}

let seq = 0;
const pending = new Map();

function send(ws, method, params = {}) {
  const id = ++seq;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function main() {
  await waitForChrome();
  const created = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" });
  const tab = await created.json();
  if (!tab.webSocketDebuggerUrl) throw new Error(`No page target: ${JSON.stringify(tab)}`);
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve);
    ws.addEventListener("error", reject);
  });
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (!msg.id || !pending.has(msg.id)) return;
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result);
  });

  await send(ws, "Page.enable");
  await send(ws, "Runtime.enable");
  const problems = [];

  for (const [id, rel, width, height] of jobs) {
    await send(ws, "Emulation.setDeviceMetricsOverride", {
      width,
      height,
      deviceScaleFactor: 1,
      mobile: false,
    });
    const url = `file://${html}?id=${id}`;
    await send(ws, "Page.navigate", { url });
    await send(ws, "Runtime.evaluate", {
      awaitPromise: true,
      expression: `new Promise((resolve) => {
        const done = () => document.fonts.ready.then(() => resolve(document.readyState));
        if (document.readyState === "complete") done();
        else window.addEventListener("load", done, { once: true });
      })`,
    });
    await send(ws, "Runtime.evaluate", {
      awaitPromise: true,
      expression: "new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r('ok'))))",
    });

    const fonts = await send(ws, "Runtime.evaluate", {
      returnByValue: true,
      expression: `({
        jakarta: document.fonts.check("800 120px Jakarta"),
        inter: document.fonts.check("600 40px Inter")
      })`,
    });
    const layout = await send(ws, "Runtime.evaluate", {
      returnByValue: true,
      expression: `(() => {
        const board = document.querySelector(".board.on");
        if (!board) return { error: "no board" };
        const foot = board.querySelector(".foot");
        const body = board.querySelector(".body");
        const br = board.getBoundingClientRect();
        const issues = [];
        if (board.scrollHeight > board.clientHeight + 2) issues.push("board-y " + board.scrollHeight + ">" + board.clientHeight);
        if (foot && body) {
          const f = foot.getBoundingClientRect();
          const b = body.getBoundingClientRect();
          if (f.bottom > br.bottom + 1) issues.push("foot-clip");
          if (b.bottom > f.top + 1) issues.push("overlap " + Math.round(b.bottom - f.top));
          let worst = null;
          for (const el of body.querySelectorAll("*")) {
            const r = el.getBoundingClientRect();
            if (r.width < 2 || r.height < 2) continue;
            const past = Math.round(r.bottom - b.bottom);
            if (past > 2 && (!worst || past > worst.past)) worst = { past, name: el.tagName + "." + el.className };
          }
          if (worst) issues.push("past-body " + worst.past + " " + worst.name);
        }
        for (const el of board.querySelectorAll(".inner, .panel")) {
          if (el.scrollHeight > el.clientHeight + 4) issues.push("clip " + el.className + " " + el.scrollHeight + ">" + el.clientHeight);
        }
        for (const el of board.querySelectorAll("h1,h2,p,li,strong,span,em,b")) {
          if (el.getClientRects().length === 0) continue;
          if (el.scrollWidth > el.clientWidth + 8) issues.push("x " + el.tagName + "." + el.className + ":" + (el.innerText || "").slice(0, 36));
        }
        return { issues, w: Math.round(br.width), h: Math.round(br.height) };
      })()`,
    });

    const fontOk = fonts.result.value;
    const lay = layout.result.value;
    const flags = [...(lay.issues || [])];
    if (!fontOk.jakarta || !fontOk.inter) flags.push("font " + JSON.stringify(fontOk));
    if (lay.w !== width || lay.h !== height) flags.push(`size ${lay.w}x${lay.h}`);
    if (flags.length) problems.push(`${id}: ${flags.join(" | ")}`);

    const shot = await send(ws, "Page.captureScreenshot", { format: "png", fromSurface: true });
    const out = resolve(root, rel);
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, Buffer.from(shot.data, "base64"));
    console.log(`${flags.length ? "WARN" : "ok  "} ${id} -> ${rel}`);
  }

  ws.close();
  chrome.kill();
  if (problems.length) {
    console.error("\nLayout flags:\n" + problems.join("\n"));
    process.exitCode = 2;
  }
}

main().catch((err) => {
  console.error(err);
  chrome.kill();
  process.exit(1);
});
