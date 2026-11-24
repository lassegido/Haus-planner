#!/usr/bin/env python3
"""Findet totes CSS in src/style.css (nur Bericht, ändert nichts). Aufruf: python3 tools/css_audit.py [--fix]

1. Selektoren mit Klassen/IDs, die im HTML und JavaScript nirgends vorkommen → können nie greifen.
2. Angaben, die eine spätere Regel mit exakt demselben Selektor im selben @media-Zusammenhang
   immer überschreibt → wirkungslos.
--fix entfernt beides. Danach immer mit tools/style_diff.py prüfen, dass sich nichts sichtbar ändert.
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "src", "style.css")
USES = [os.path.join(ROOT, "src", "seite.html")] + sorted(glob.glob(os.path.join(ROOT, "src", "js", "*.js")))
# Werte mit neuer Syntax: ältere Browser verwerfen sie, dann greift die frühere Angabe als Rückfall → nicht entfernen
MODERN = re.compile(r"dvh|svh|lvh|dvw|color-mix|oklch|light-dark|\blch\(|\blab\(|env\(|:has\(|@supports")


def parse(css, base=0):
    """Zerlegt CSS in Regeln. Liefert Liste von dicts: ctx (Tupel der @-Bedingungen), sel, start, end, body_start, decls."""
    rules, stack, i, n = [], [], 0, len(css)
    pre = 0  # Beginn des aktuellen Selektors/Präludiums
    while i < n:
        c = css[i]
        if css.startswith("/*", i):
            j = css.index("*/", i + 2) + 2
            if css[pre:i].strip() == "":
                pre = j
            i = j
            continue
        if c in "\"'":
            j = i + 1
            while css[j] != c:
                j += 2 if css[j] == "\\" else 1
            i = j + 1
            continue
        if c == "{":
            prelude = css[pre:i].strip()
            if prelude.startswith("@") and not prelude.startswith(("@font-face", "@page")) and not re.match(r"@keyframes|@-webkit-keyframes", prelude):
                stack.append(prelude)
                i += 1
                pre = i
                continue
            # Blattregel: bis zur passenden }
            depth, j = 1, i + 1
            while depth:
                if css.startswith("/*", j):
                    j = css.index("*/", j + 2) + 2
                    continue
                if css[j] in "\"'":
                    q, j = css[j], j + 1
                    while css[j] != q:
                        j += 2 if css[j] == "\\" else 1
                    j += 1
                    continue
                depth += {"{": 1, "}": -1}.get(css[j], 0)
                j += 1
            start = base + pre + (len(css[pre:i]) - len(css[pre:i].lstrip()))
            rules.append({"ctx": tuple(stack), "sel": " ".join(prelude.split()), "start": start, "end": base + j,
                          "body_start": base + i + 1, "body": css[i + 1:j - 1], "kind": "at" if prelude.startswith("@") else "style"})
            i = j
            pre = i
            continue
        if c == "}":
            stack.pop()
            i += 1
            pre = i
            continue
        i += 1
    for r in rules:
        r["decls"] = decls(r["body"], r["body_start"]) if r["kind"] == "style" else []
    return rules


def decls(body, base):
    """Angaben einer Regel mit Position: (eigenschaft, wert, wichtig, start, ende)."""
    out, i, start, n = [], 0, 0, len(body)
    while i <= n:
        c = body[i] if i < n else ";"
        if i < n and c in "\"'":
            j = i + 1
            while body[j] != c:
                j += 2 if body[j] == "\\" else 1
            i = j + 1
            continue
        if i < n and c == "(":
            depth, j = 1, i + 1
            while depth:
                depth += {"(": 1, ")": -1}.get(body[j], 0)
                j += 1
            i = j
            continue
        if c == ";":
            raw = body[start:i]
            if ":" in raw and raw.strip():
                prop, val = raw.split(":", 1)
                imp = bool(re.search(r"!\s*important\s*$", val))
                lead = len(raw) - len(raw.lstrip())
                out.append((prop.strip().lower(), val.strip(), imp, base + start + lead, base + min(i + 1, n)))
            start = i + 1
        i += 1
    return out


def split_selectors(sel):
    out, depth, cur = [], 0, ""
    for c in sel:
        depth += {"(": 1, ")": -1}.get(c, 0)
        if c == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += c
    out.append(cur.strip())
    return out


def load():
    css = open(CSS, encoding="utf-8").read()
    other = "".join(open(p, encoding="utf-8").read() for p in USES)
    return css, other


def audit():
    s, other = load()
    rules = parse(s)
    words = set(re.findall(r"[A-Za-z_][\w-]*", other))
    # Klassen, die im Code zusammengesetzt werden („p${prio}“, "st-"+x): Präfixe sammeln, solche Treffer nur melden, nicht entfernen
    prefixes = set(re.findall(r"(?<=[\"'`\s])([A-Za-z_][\w-]*)(?:\$\{|[\"']\s*\+)", other))
    dead_sel, dead_decl, unsure = [], [], []
    for r in rules:
        if r["kind"] != "style" or any(c.startswith(("@keyframes", "@font-face")) for c in r["ctx"]):
            continue
        sels = split_selectors(r["sel"])
        gone = []
        for x in sels:
            tokens = re.findall(r"[.#]([A-Za-z_][\w-]*)", re.sub(r"\[[^\]]*\]|\"[^\"]*\"", "", x))
            missing = [t for t in tokens if t not in words]
            if missing and any(maybe_dynamic(t, prefixes) for t in missing):
                unsure.append((r, x, missing))
            elif missing:
                gone.append((x, missing))
        if gone:
            dead_sel.append((r, sels, gone))
    # Überschriebene Angaben: gleicher Zusammenhang, exakt gleicher Selektor, gleiche Eigenschaft, später
    for i, r in enumerate(rules):
        if r["kind"] != "style":
            continue
        later = [q for q in rules[i + 1:] if q["kind"] == "style" and q["ctx"] == r["ctx"] and q["sel"] == r["sel"]]
        if not later:
            continue
        for (p, v, imp, st, en) in r["decls"]:
            if p.startswith("--"):
                continue
            for q in later:
                hit = [(qp, qv, qi) for (qp, qv, qi, _, _) in q["decls"] if qp == p]
                if hit and (hit[-1][2] or not imp) and not MODERN.search(hit[-1][1]):
                    dead_decl.append((r, (p, v, imp, st, en), q))
                    break
    return s, rules, dead_sel, dead_decl, unsure


def drop_empty(css):
    """Leere Regeln („.x{}“), leere @media-Blöcke und doppelte Leerzeilen entfernen."""
    while True:
        new = re.sub(r"(?:(?<=[}{;\n])|^)[ \t]*[^{}@;\n][^{};]*\{\s*\}", "", css)
        new = re.sub(r"@(?:media|supports)[^{}]*\{\s*\}", "", new)
        if new == css:
            break
        css = new
    css = re.sub(r"\n[ \t]*(?=\n)", "\n", css)
    css = re.sub(r"\n{3,}", "\n\n", css)
    return re.sub(r";\}", "}", css)


def maybe_dynamic(token, prefixes):
    """Könnte der Code diese Klasse zusammensetzen? Kurzes Präfix nur bei Ziffern danach („p${prio}“ → p1)."""
    for pf in prefixes:
        rest = token[len(pf):]
        if token.startswith(pf) and rest and (rest.isdigit() or len(pf) >= 3):
            return True
    return False


def line(s, pos):
    return s.count("\n", 0, pos) + 1


def main():
    s, rules, dead_sel, dead_decl, unsure = audit()
    print("%d CSS-Regeln" % sum(1 for r in rules if r["kind"] == "style"))
    print("\nSelektoren, die nie greifen können (%d Regeln):" % len(dead_sel))
    for r, sels, gone in dead_sel:
        print("  Z. %-5d %s  ← fehlt: %s" % (line(s, r["start"]), " , ".join(x for x, _ in gone)[:110], ", ".join(sorted({m for _, ms in gone for m in ms}))))
    print("\nUnsicher, weil Klassen im Code zusammengesetzt werden (bleiben stehen, %d):" % len(unsure))
    for r, x, missing in unsure:
        print("  Z. %-5d %s  ← %s" % (line(s, r["start"]), x[:80], ", ".join(missing)))
    print("\nÜberschriebene Angaben (%d):" % len(dead_decl))
    for r, (p, v, imp, st, en), q in dead_decl:
        print("  Z. %-5d %-40s %s:%s  → Z. %d" % (line(s, st), r["sel"][:40], p, v[:30], line(s, q["start"])))
    if "--fix" in sys.argv:
        cuts = []
        for r, sels, gone in dead_sel:
            keep = [x for x in sels if x not in {g for g, _ in gone}]
            if keep:
                cuts.append((r["start"], r["body_start"] - 1, ",".join(keep)))
            else:
                cuts.append((r["start"], r["end"], ""))
        whole = [(a, b) for a, b, t in cuts if t == ""]
        for r, (p, v, imp, st, en), q in dead_decl:
            if not any(a <= st < b for a, b in whole):
                cuts.append((st, en, ""))
        out, last = [], 0
        for a, b, t in sorted(cuts):
            if a < last:
                continue
            out.append(s[last:a])
            out.append(t)
            last = b
        out.append(s[last:])
        new = "".join(out)
        new = drop_empty(new)
        open(CSS, "w", encoding="utf-8").write(new)
        print("\nEntfernt: %d Regeln/Selektoren, %d Angaben. Jetzt tools/style_diff.py compare ausführen." % (len(dead_sel), len(dead_decl)))


if __name__ == "__main__":
    main()
