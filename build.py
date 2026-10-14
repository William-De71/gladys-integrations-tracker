#!/usr/bin/env python3
"""Build the tracker: Pierre-Gilles' Home Assistant list ↔ Gladys external integrations.

Sources, read again on every run:
  - Pierre-Gilles' gist (3_full-list.csv);
  - the live Gladys store index (index.json);
  - GitHub repositories with the gladys-assistant-integration topic (via `gh`);
  - data/extra-repos.txt: Gladys repositories spotted by hand, without the topic;
  - data/mapping.txt: HA list number → Gladys repository (E = equivalent, P = partial);
  - data/claims.txt: forum claims that have no repository yet.

Output, in site/: data.json (read by index.html), one CSV per table, and an .xlsx workbook.
"""
import csv
import io
import json
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "site"

GIST_ID = "9c4ba77a0faa47c4ea67c74351db9094"
GIST_URL = f"https://gist.github.com/Pierre-Gilles/{GIST_ID}"
# The raw URL needs no token: the Actions GITHUB_TOKEN cannot read the gists API.
GIST_CSV = f"https://gist.githubusercontent.com/Pierre-Gilles/{GIST_ID}/raw/3_full-list.csv"
STORE_INDEX = "https://integration-store-storage.gladysassistant.com/index.json"
STORE_PAGE = "https://gladysassistant.com/fr/docs/integrations/external/"
FORUM_TOPIC = "https://community.gladysassistant.com/t/10385"
TOPIC = "gladys-assistant-integration"
USER_AGENT = "gladys-integrations-tracker"

# Status keys, from the most to the least advanced. The page and the workbook translate them.
STORE, TOPIC_ONLY, NO_TOPIC, CLAIMED, FREE = "store", "topic", "no_topic", "claimed", "free"
STATUS_FR = {
    STORE: "Publiée (store)",
    TOPIC_ONLY: "Dépôt GitHub, pas encore au store",
    NO_TOPIC: "Dépôt GitHub sans topic store",
    CLAIMED: "Revendiquée (forum)",
    FREE: "Libre",
}
RANK = [STORE, TOPIC_ONLY, NO_TOPIC]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def gh_api(*args):
    result = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def read_table(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            rows.append([c.strip() for c in line.split("|")])
    return rows


def load_ha_list():
    return list(csv.DictReader(io.StringIO(fetch(GIST_CSV))))


def find_cover(repo, branch):
    for name in ("cover.png", "cover.jpg"):
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/{name}"
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    return url
        except Exception:
            pass
    return ""


def load_gladys():
    index = json.loads(fetch(STORE_INDEX))
    repos = {}
    for item in index["integrations"]:
        m = item["manifest"]
        repo = item["repo_url"].replace("https://github.com/", "")
        desc = m.get("description") or {}
        repos[repo.lower()] = dict(
            repo=repo, name=m["name"], author=repo.split("/")[0],
            desc_fr=desc.get("fr") or desc.get("en", ""), desc_en=desc.get("en") or desc.get("fr", ""),
            type=m.get("type", ""), version=m.get("version", ""), cover=item.get("cover_url", ""),
            status=STORE, since=(item.get("first_seen_at") or "")[:10],
            pushed=(item.get("github") or {}).get("pushed_at", "")[:10],
        )

    pages = gh_api("-X", "GET", "search/repositories", "-f", f"q=topic:{TOPIC}", "-f", "per_page=100",
                   "--paginate", "--jq", ".items[]")
    candidates = [(json.loads(line), TOPIC_ONLY) for line in pages.splitlines() if line.strip()]
    for line in (DATA / "extra-repos.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line.lower() not in repos:
            try:
                candidates.append((json.loads(gh_api(f"repos/{line}")), NO_TOPIC))
            except RuntimeError:
                print(f"repository not found: {line}", file=sys.stderr)

    new = []
    for r, status in candidates:
        key = r["full_name"].lower()
        if key in repos:
            continue
        desc = r.get("description") or ""
        repos[key] = dict(
            repo=r["full_name"], name=r["name"], author=r["owner"]["login"], desc_fr=desc, desc_en=desc,
            type="", version="", cover="", status=status,
            since=r["created_at"][:10], pushed=r["pushed_at"][:10],
            _branch=r.get("default_branch", "main"),
        )
        new.append(repos[key])
    with ThreadPoolExecutor(16) as ex:
        for g, cover in zip(new, ex.map(lambda g: find_cover(g["repo"], g["_branch"]), new)):
            g["cover"] = cover
            del g["_branch"]
    return repos, index.get("generated_at", "")


def build():
    ha = load_ha_list()
    gladys, index_date = load_gladys()

    mapping = {}
    for num, repo, quality in read_table(DATA / "mapping.txt"):
        g = gladys.get(repo.lower())
        if g is None:
            print(f"mapping skipped, unknown repository: {repo}", file=sys.stderr)
            continue
        mapping.setdefault(num, []).append((g, quality))
    claims = {num: (who, src) for num, who, src in read_table(DATA / "claims.txt")}

    ha_rows = []
    for h in ha:
        num = h["#"]
        matches = sorted(mapping.get(num, []), key=lambda m: (RANK.index(m[0]["status"]), m[1]))
        row = dict(
            n=int(num), prio=h["Priority"], name=h["Integration"], category=h["Category"],
            usage=h["HA usage (% of installations)"], access=h["Access"],
            no_hardware=h["No hardware needed"] == "yes", area=h["Area"], link=h["Reference link"],
            desc=h["Description"], status=FREE, quality="", claim="",
            matches=[dict(repo=g["repo"], quality=q) for g, q in matches],
        )
        if matches:
            row["status"] = matches[0][0]["status"]
            row["quality"] = matches[0][1]
        elif num in claims:
            row["status"] = CLAIMED
            row["claim"] = " — ".join(claims[num])
        elif h["Status"] != "Available":
            row["status"] = CLAIMED
            row["claim"] = f"gist: {h['Status']}"
        ha_rows.append(row)

    for g in gladys.values():
        g["ha"] = sorted((int(n) for n, lst in mapping.items() if any(x is g for x, _ in lst)))
    gladys_rows = sorted(gladys.values(), key=lambda g: (RANK.index(g["status"]), g["name"].lower()))

    return dict(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        store_index_at=index_date,
        sources=dict(ha_list=GIST_URL, store=STORE_PAGE, store_index=STORE_INDEX, forum=FORUM_TOPIC,
                     topic=f"https://github.com/topics/{TOPIC}"),
        ha=ha_rows,
        gladys=gladys_rows,
    )


def flat_tables(data):
    """Plain values, so that the CSVs work with Google Sheets' IMPORTDATA."""
    by_repo = {g["repo"]: g for g in data["gladys"]}
    head_ha = ["N°", "Prio", "Intégration Home Assistant", "Catégorie", "Usage HA", "Accès",
               "Sans matériel", "Zone", "Doc HA / HACS", "Statut Gladys", "Correspondance",
               "Intégration Gladys", "Auteur", "Dépôt GitHub", "Cover", "Version", "Doublon",
               "Autres dépôts / note", "Description HA"]
    rows_ha = []
    for h in data["ha"]:
        first = by_repo[h["matches"][0]["repo"]] if h["matches"] else None
        others = [m["repo"] for m in h["matches"][1:]]
        rows_ha.append([
            h["n"], h["prio"], h["name"], h["category"], h["usage"], h["access"],
            "oui" if h["no_hardware"] else "", h["area"], h["link"], STATUS_FR[h["status"]],
            {"E": "Équivalente", "P": "Partielle"}.get(h["quality"], ""),
            first["name"] if first else "", first["author"] if first else "",
            f"https://github.com/{first['repo']}" if first else "",
            first["cover"] if first else "", first["version"] if first else "",
            f"oui ({len(h['matches'])})" if others else "",
            ", ".join(others) or h["claim"], h["desc"],
        ])
    head_g = ["Intégration Gladys", "Auteur", "Dépôt GitHub", "Cover", "Statut", "Type", "Version",
              "Vue depuis", "Dernier push", "Équivalent HA (liste)", "Description"]
    names = {h["n"]: h["name"] for h in data["ha"]}
    rows_g = [[g["name"], g["author"], f"https://github.com/{g['repo']}", g["cover"], STATUS_FR[g["status"]],
               g["type"], g["version"], g["since"], g["pushed"],
               ", ".join(f"{n} {names[n]}" for n in g["ha"]) or "hors liste", g["desc_fr"]]
              for g in data["gladys"]]
    return (head_ha, rows_ha), (head_g, rows_g)


def write_xlsx(data, tables, path):
    (head_ha, rows_ha), (head_g, rows_g) = tables
    n_taken = sum(1 for h in data["ha"] if h["status"] != FREE)
    p1 = [h for h in data["ha"] if h["prio"] == "P1"]
    n_dup = sum(1 for h in data["ha"] if len(h["matches"]) > 1)
    n_store = sum(1 for g in data["gladys"] if g["status"] == STORE)

    def link(url, label=None):
        return f'=HYPERLINK("{url}","{label or url}")' if url else ""

    wb = Workbook()
    ws = wb.active
    ws.title = "Lisez-moi"
    for r in [
        ["Suivi des intégrations externes Gladys"],
        [f"Généré le {data['generated_at'][:16].replace('T', ' ')} UTC "
         f"(index du store : {data['store_index_at'][:16].replace('T', ' ')} UTC)"],
        [],
        ["Liste Home Assistant (gist de Pierre-Gilles)",
         f"{len(data['ha'])} idées, dont {n_taken} prises ou faites ; "
         f"P1 : {sum(1 for h in p1 if h['status'] != FREE)} / {len(p1)}"],
        ["Intégrations Gladys repérées", f"{len(data['gladys'])} dépôts, dont {n_store} publiés au store"],
        ["Idées avec plusieurs dépôts (doublons)", str(n_dup)],
        [],
        ["Statuts"],
        [STATUS_FR[STORE], "indexée par le store Gladys"],
        [STATUS_FR[TOPIC_ONLY], f"dépôt avec le topic {TOPIC}, pas encore indexé (en cours, ou refusé par l'indexeur)"],
        [STATUS_FR[NO_TOPIC], "dépôt trouvé sur GitHub sans le topic : en cours, ou topic oublié"],
        [STATUS_FR[CLAIMED], "annoncée sur le forum, aucun dépôt trouvé"],
        [STATUS_FR[FREE], "personne dessus à notre connaissance"],
        [],
        ["Correspondance", "Équivalente : couvre l'intégration HA. Partielle : en couvre une partie."],
        ["Hors liste", "intégration Gladys sans entrée dans la liste : la liste a retiré ce que Gladys "
                       "couvrait déjà, et certaines n'existent pas chez HA"],
        [],
        ["Sources"],
        ["Liste Home Assistant", link(GIST_URL)],
        ["Store Gladys", link(STORE_PAGE)],
        ["Fil forum", link(FORUM_TOPIC)],
        ["Dépôts GitHub", link(f"https://github.com/topics/{TOPIC}", f"topic {TOPIC}")],
    ]:
        ws.append(r)
    ws["A1"].font = Font(bold=True, size=14)
    for cell in ("A8", "A18"):
        ws[cell].font = Font(bold=True)
    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["B"].width = 110

    fills = {STATUS_FR[STORE]: "C6EFCE", STATUS_FR[TOPIC_ONLY]: "FFEB9C",
             STATUS_FR[NO_TOPIC]: "FCE4D6", STATUS_FR[CLAIMED]: "DDEBF7"}
    sheets = [
        ("Liste HA ↔ Gladys", head_ha, rows_ha, 9, {8: "doc", 13: None}, 14,
         [6, 5, 34, 24, 9, 12, 9, 14, 6, 26, 13, 26, 16, 38, 22, 9, 10, 34, 60]),
        ("Intégrations Gladys", head_g, rows_g, 4, {2: None}, 3,
         [28, 16, 40, 22, 26, 13, 9, 11, 11, 40, 70]),
    ]
    for title, head, rows, status_col, link_cols, cover_col, widths in sheets:
        ws = wb.create_sheet(title)
        ws.append(head)
        for r in rows:
            r = list(r)
            for col, label in link_cols.items():
                if r[col]:
                    r[col] = link(r[col], label or r[col].replace("https://github.com/", ""))
            r[cover_col] = f'=IMAGE("{r[cover_col]}")' if r[cover_col] else ""
            ws.append(r)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="1F4E78")
            c.alignment = Alignment(vertical="center", wrap_text=True)
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for i, r in enumerate(rows, 2):
            if r[status_col] in fills:
                ws.cell(i, status_col + 1).fill = PatternFill("solid", fgColor=fills[r[status_col]])
            if r[cover_col]:
                ws.row_dimensions[i].height = 60
        ws.freeze_panes = "D2" if title.startswith("Liste") else "B2"
        ws.auto_filter.ref = ws.dimensions
    wb.save(path)


def main():
    data = build()
    OUT.mkdir(exist_ok=True)
    (OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    tables = flat_tables(data)
    for name, (head, rows) in zip(("liste-ha-gladys.csv", "integrations-gladys.csv"), tables):
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rows)
    write_xlsx(data, tables, OUT / "suivi-integrations-gladys.xlsx")
    shutil.copy(ROOT / "index.html", OUT / "index.html")

    n_taken = sum(1 for h in data["ha"] if h["status"] != FREE)
    n_dup = sum(1 for h in data["ha"] if len(h["matches"]) > 1)
    unmapped = [g["repo"] for g in data["gladys"] if not g["ha"] and g["status"] != STORE]
    print(f"{len(data['ha'])} HA ideas ({n_taken} taken), {len(data['gladys'])} Gladys repositories, "
          f"{n_dup} duplicates; {len(unmapped)} repositories outside the store and not mapped")


if __name__ == "__main__":
    main()
