// Planner: Homescreen-Widget für die App "Scriptable" (Anzeige der eigenen Aufgaben)
const BASE = "__BASE__";
const WHO = args.widgetParameter || "__WHO__";
const fam = config.widgetFamily || "medium";
const MAX = { small: 4, medium: 6, large: 12, extraLarge: 14 }[fam] || 6;
const ink = Color.dynamic(new Color("#14303F"), new Color("#F5F3EB"));
const mut = Color.dynamic(new Color("#587080"), new Color("#9FB0B9"));
const bg = Color.dynamic(new Color("#F5F3EB"), new Color("#0E222D"));
const COL = { todo: "#6CB6E4", doing: "#F29A2E", done: "#387CA3" };
const SYM = { todo: "○", doing: "◐", done: "●" };
const key = "planner_widget_cache";
let d = null, stale = false;
try {
  const r = new Request(BASE + "/api/widget?who=" + encodeURIComponent(WHO));
  r.timeoutInterval = 8;
  d = await r.loadJSON();
  d.at = new Date().toISOString();
  Keychain.set(key, JSON.stringify(d));
} catch (e) {
  try { d = JSON.parse(Keychain.get(key)); stale = true; } catch (e2) { d = null; }
}
const w = new ListWidget();
w.backgroundColor = bg;
w.setPadding(12, 14, 10, 14);
w.url = BASE + "/";
const head = w.addStack();
head.centerAlignContent();
const t = head.addText("Meine Aufgaben");
t.font = Font.boldSystemFont(fam === "small" ? 13 : 15);
t.textColor = ink;
head.addSpacer();
if (d) {
  const n = d.groups.reduce((a, g) => a + g.tasks.length, 0);
  const c = head.addText(String(n));
  c.font = Font.boldSystemFont(15);
  c.textColor = new Color("#D35526");
}
w.addSpacer(6);
if (!d) {
  const e = w.addText("Planner nicht erreichbar. Bitte im Heimnetz verbunden sein.");
  e.font = Font.systemFont(12);
  e.textColor = mut;
} else if (!d.groups.length) {
  const e = w.addText("Nichts geplant. Schönen Tag!");
  e.font = Font.systemFont(13);
  e.textColor = mut;
} else {
  let shown = 0;
  for (const g of d.groups) {
    if (shown >= MAX) break;
    const h = w.addText(g.t.toUpperCase());
    h.font = Font.boldSystemFont(9);
    h.textColor = g.k === "late" ? new Color("#D35526") : mut;
    shown += 0.6;
    for (const k of g.tasks) {
      if (shown >= MAX) break;
      const row = w.addStack();
      row.centerAlignContent();
      row.spacing = 5;
      const s = row.addText(SYM[k.status] || "○");
      s.font = Font.systemFont(13);
      s.textColor = new Color(COL[k.status] || COL.todo);
      if (k.prio === 1) {
        const p = row.addText("!");
        p.font = Font.boldSystemFont(12);
        p.textColor = new Color("#B3411A");
      }
      const tt = row.addText(k.title);
      tt.font = Font.mediumSystemFont(fam === "small" ? 12 : 13);
      tt.textColor = ink;
      tt.lineLimit = 1;
      shown += 1;
    }
  }
}
w.addSpacer();
if (stale && d) {
  const s = w.addText("Offline, Stand " + new Date(d.at).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }));
  s.font = Font.systemFont(9);
  s.textColor = mut;
}
w.refreshAfterDate = new Date(Date.now() + 15 * 60 * 1000);
if (config.runsInWidget) Script.setWidget(w);
else await w[fam === "small" ? "presentSmall" : fam === "large" ? "presentLarge" : "presentMedium"]();
Script.complete();
