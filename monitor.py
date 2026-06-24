# monitor.py
import feedparser
import json
import os
from datetime import datetime, date
from email.utils import parsedate_to_datetime
import importlib.util

# =========================
# CONFIGURAÇÃO
# =========================

feeds = [
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.securityweek.com/feed/",
    "https://www.helpnetsecurity.com/feed/",
    "https://www.infosecurity-magazine.com/rss/news/",
    "https://www.darkreading.com/rss.xml",
    "https://www.csoonline.com/index.rss",
    "https://www.techradar.com/rss",
    "https://www.zdnet.com/news/rss.xml",
]

CACHE_FILE = "cache_noticias.json"
TECN_FILE = "tecnologias.txt"
MATCH_FILE = "match_rules.py"


# =========================
# CARREGAR MATCH EXTERNO
# =========================

def carregar_match():
    spec = importlib.util.spec_from_file_location("match_rules", MATCH_FILE)
    match_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(match_module)
    return match_module.match_produto


match_produto = carregar_match()


# =========================
# TECNOLOGIAS
# =========================

def carregar_tecnologias(arquivo=TECN_FILE):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    except:
        return []


# =========================
# DATA
# =========================

def parse_data(data_str):
    try:
        if not data_str:
            return None
        return parsedate_to_datetime(data_str)
    except:
        return None


def formatar_data(dt):
    if not dt:
        return "N/A"
    return dt.strftime("%d/%m/%Y")


def is_today(dt):
    if not dt:
        return False
    return dt.date() == date.today()


# =========================
# CACHE
# =========================

def carregar_cache():
    if not os.path.exists(CACHE_FILE):
        return []
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def ja_existe(cache, link):
    return any(n["link"] == link for n in cache)


# =========================
# BUSCAR FEEDS
# =========================

def buscar_noticias(produtos, feeds, cache):

    novas = []

    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)

            for item in feed.entries:

                if ja_existe(cache, item.link):
                    continue

                texto = f"{item.title} {item.get('summary', '')}"

                data_dt = parse_data(item.get("published", ""))

                for produto in produtos:

                    if match_produto(texto, produto):

                        noticia = {
                            "produto": produto,
                            "titulo": item.title,
                            "link": item.link,
                            "data_dt": item.get("published", ""),
                            "data_fmt": formatar_data(data_dt),
                            "is_today": is_today(data_dt),
                            "resumo": item.get("summary", "")[:300],
                            "fonte": feed.feed.get("title", feed_url)
                        }

                        novas.append(noticia)
                        cache.append(noticia)

        except:
            pass

    return novas


# =========================
# HTML
# =========================

def gerar_html(noticias, feeds, produtos):

    noticias.sort(key=lambda x: x.get("is_today", False), reverse=True)

    data_hoje = datetime.now().strftime("%d/%m/%Y")

    options_produtos = "\n".join([f'<option value="{p}">{p}</option>' for p in produtos])

    datas = sorted(set([n["data_fmt"] for n in noticias if n["data_fmt"] != "N/A"]), reverse=True)
    options_datas_html = "\n".join([f'<option value="{d}">{d}</option>' for d in datas])

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cyber Security Monitor</title>

<style>
body {{
    font-family: Arial;
    margin: 0;
    background: #f4f6f9;
}}
header {{
    background: #0f172a;
    color: white;
    padding: 20px;
}}
.container {{
    width: 90%;
    max-width: 1200px;
    margin: 30px auto;
}}
.dashboard {{
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}}
.card {{
    flex: 1;
    background: white;
    padding: 15px;
    border-radius: 10px;
}}
.card h2 {{
    color: #2563eb;
}}
.news-card {{
    background: white;
    padding: 20px;
    margin-bottom: 15px;
    border-radius: 10px;
}}
.meta {{
    font-size: 13px;
    color: #666;
}}
.tag {{
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    padding: 4px 8px;
    border-radius: 5px;
    font-size: 12px;
}}
.filters {{
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}}
select {{
    width: 100%;
    padding: 10px;
    border-radius: 8px;
}}
a {{
    color: #2563eb;
}}
footer {{
    text-align: center;
    padding: 30px;
    color: #666;
}}
</style>
</head>

<body>

<header>
    <h1>Cyber Security Monitor</h1>
    <p>Atualizado em {data_hoje}</p>
</header>

<div class="container">

<div class="dashboard">
    <div class="card">
        <h2>{len(noticias)}</h2>
        <p>Notícias</p>
    </div>
    <div class="card">
        <h2>{len(produtos)}</h2>
        <p>Tecnologias</p>
    </div>
    <div class="card">
        <h2>{len(feeds)}</h2>
        <p>Feeds</p>
    </div>
</div>

<div class="filters">
<select id="filtroProduto" onchange="filtrar()">
<option value="">Tecnologia</option>
{options_produtos}
</select>

<select id="filtroData" onchange="filtrar()">
<option value="">Data</option>
{options_datas_html}
</select>
</div>

<div id="listaNoticias">
"""

    for n in noticias:

        html += f"""
        <div class="news-card item">

            <div class="tag produto">{n['produto']}</div>

            <h3>{n['titulo']}</h3>

            <div class="meta data">
                Fonte: {n['fonte']} | Data: {n['data_fmt']}
            </div>

            <p>{n['resumo']}</p>

            <a href="{n['link']}" target="_blank">Abrir notícia</a>

        </div>
        """

    html += """
</div>

</div>

<footer>Relatório gerado automaticamente</footer>

<script>
function filtrar() {
    let produto = document.getElementById("filtroProduto").value.toLowerCase();
    let data = document.getElementById("filtroData").value.toLowerCase();

    let items = document.getElementsByClassName("item");

    for (let i = 0; i < items.length; i++) {

        let p = items[i].getElementsByClassName("produto")[0].innerText.toLowerCase();
        let d = items[i].getElementsByClassName("data")[0].innerText.toLowerCase();

        let okP = produto === "" || p.includes(produto);
        let okD = data === "" || d.includes(data);

        items[i].style.display = (okP && okD) ? "block" : "none";
    }
}
</script>

</body>
</html>
"""

    return html


# =========================
# MAIN
# =========================

def main():

    produtos = carregar_tecnologias()
    cache = carregar_cache()

    buscar_noticias(produtos, feeds, cache)

    salvar_cache(cache)

    html = gerar_html(cache, feeds, produtos)

    with open("relatorio.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("OK - executado com match externo e cache")
    print(f"Total cache: {len(cache)}")


if __name__ == "__main__":
    main()
