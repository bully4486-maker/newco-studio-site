import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(root, "shots");
mkdirSync(outDir, { recursive: true });
const port = 9344;

const jobs = [
  ["hearth-hero", "https://studio.newcopacks.co.uk/demos/hearth-and-crumb/", ""],
  ["paws-hero", "https://studio.newcopacks.co.uk/demos/paws-parlour/", ""],
  ["halvercroft-hero", "https://studio.newcopacks.co.uk/demos/halvercroft-electrical/", ""],
];

const chrome = spawn("google-chrome", [
  "--headless=new",
  "--no-sandbox",
  "--disable-gpu",
  "--disable-dev-shm-usage",
  "--hide-scrollbars",
  `--remote-debugging-port=${port}`,
  "--user-data-dir=/tmp/newco-shot-chrome",
  "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitForChrome() {
  for (let i = 0; i < 60; i++) {
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
  await send(ws, "Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    mobile: true,
  });
  await send(ws, "Emulation.setUserAgentOverride", {
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
  });

  for (const [name, url, anchor] of jobs) {
    await send(ws, "Page.navigate", { url });
    await send(ws, "Runtime.evaluate", {
      awaitPromise: true,
      expression: `Promise.race([
        new Promise((resolve) => {
          const ready = () => {
            const hero = document.querySelector("img");
            const heroReady = !hero || hero.complete
              ? Promise.resolve()
              : new Promise((r) => { hero.addEventListener("load", r, {once:true}); hero.addEventListener("error", r, {once:true}); });
            Promise.race([
              Promise.all([document.fonts.ready, heroReady]),
              new Promise((r) => setTimeout(r, 5000)),
            ]).then(() => setTimeout(resolve, 600));
          };
          if (document.readyState === "complete") ready();
          else window.addEventListener("load", ready, { once: true });
        }),
        new Promise((resolve) => setTimeout(resolve, 12000)),
      ])`,
    });
    if (anchor) {
      await send(ws, "Runtime.evaluate", {
        awaitPromise: true,
        expression: `(() => {
          const el = document.getElementById(${JSON.stringify(anchor)});
          if (el) el.scrollIntoView({ block: "start" });
          return Promise.race([
            Promise.all([...document.images].filter(i => i.getBoundingClientRect().top < innerHeight + 40).map(i => i.complete ? 1 : new Promise(r => { i.addEventListener("load", r, {once:true}); i.addEventListener("error", r, {once:true}); }))),
            new Promise(r => setTimeout(r, 4000)),
          ]).then(() => new Promise(r => setTimeout(r, 400)));
        })()`,
      });
    }
    const shot = await send(ws, "Page.captureScreenshot", { format: "png", fromSurface: true });
    const file = resolve(outDir, `${name}.png`);
    writeFileSync(file, Buffer.from(shot.data, "base64"));
    console.log("saved", name, shot.data.length);
  }
  ws.close();
  chrome.kill();
}

main().catch((err) => {
  console.error(err);
  chrome.kill();
  process.exit(1);
});
