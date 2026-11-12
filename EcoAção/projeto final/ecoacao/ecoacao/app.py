"""
EcoAção - back end (Flask, Python 3.12)

Rotas:
  /                      formulário de pesquisa
  /buscar?q=             pesquisa de local (Nominatim) -> lista de candidatos
  /diagnostico?...       diagnóstico de emissões (Climate TRACE) + ONGs
  /ongs                  diretório de ONGs (SQLite local)
  /ongs/nova             cadastro de ONG
  /fontes                fontes e limitações
  /debug/climatetrace    resposta crua da API (para ajustar o parser)
"""
import os
import re
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests
from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

from iso_countries import iso2_para_iso3

# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTATO = os.environ.get("ECOACAO_CONTATO", "contato-nao-configurado")
USER_AGENT = f"EcoAcao/0.1 (projeto educacional; {CONTATO})"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# A API do Climate TRACE é beta. Tentamos v7 e, se falhar, v6.
CLIMATETRACE_BASES = os.environ.get(
    "CLIMATETRACE_BASES",
    "https://api.climatetrace.org/v7,https://api.climatetrace.org/v6",
).split(",")

ANO_MIN, ANO_MAX = 2015, 2024
ANO_PADRAO = 2024

SETORES = {
    "power": "Energia elétrica",
    "transportation": "Transportes",
    "agriculture": "Agropecuária",
    "manufacturing": "Indústria",
    "fossil-fuel-operations": "Combustíveis fósseis",
    "buildings": "Edificações",
    "waste": "Resíduos",
    "mineral-extraction": "Mineração",
    "forestry-and-land-use": "Florestas e uso do solo",
    "fluorinated-gases": "Gases fluorados",
}

TIMEOUT = (5, 20)  # (conexão, leitura) em segundos


# --------------------------------------------------------------------------
# Cache simples com validade
# --------------------------------------------------------------------------
class CacheTTL:
    def __init__(self):
        self._dados = {}
        self._lock = threading.Lock()

    def get(self, chave):
        with self._lock:
            item = self._dados.get(chave)
            if not item:
                return None
            expira, valor = item
            if expira < time.time():
                del self._dados[chave]
                return None
            return valor

    def set(self, chave, valor, ttl):
        with self._lock:
            self._dados[chave] = (time.time() + ttl, valor)


cache = CacheTTL()


# --------------------------------------------------------------------------
# Acesso HTTP (isolado para facilitar testes)
# --------------------------------------------------------------------------
class ErroExterno(Exception):
    """Falha ao consultar uma fonte externa."""


def http_get_json(url, params=None):
    try:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        raise ErroExterno(f"Falha de rede ao acessar {urlparse(url).netloc}: {e.__class__.__name__}")
    if r.status_code != 200:
        raise ErroExterno(f"{urlparse(url).netloc} respondeu HTTP {r.status_code}")
    try:
        return r.json()
    except ValueError:
        raise ErroExterno(f"{urlparse(url).netloc} devolveu uma resposta que não é JSON")


# --------------------------------------------------------------------------
# Nominatim (política de uso: máx. 1 requisição/segundo, User-Agent próprio)
# --------------------------------------------------------------------------
_nominatim_lock = threading.Lock()
_nominatim_ultimo = 0.0


def buscar_locais(consulta):
    consulta = consulta.strip()
    chave = ("nominatim", consulta.lower())
    em_cache = cache.get(chave)
    if em_cache is not None:
        return em_cache

    global _nominatim_ultimo
    with _nominatim_lock:
        espera = 1.1 - (time.time() - _nominatim_ultimo)
        if espera > 0:
            time.sleep(espera)
        try:
            bruto = http_get_json(NOMINATIM_URL, {
                "q": consulta, "format": "jsonv2", "addressdetails": 1,
                "limit": 5, "accept-language": "pt-BR",
            })
        finally:
            _nominatim_ultimo = time.time()

    resultados = []
    for item in bruto if isinstance(bruto, list) else []:
        end = item.get("address") or {}
        cc = (end.get("country_code") or "").upper()
        cidade = next((end.get(chave) for chave in
                       ("city", "town", "village", "municipality", "county")
                       if end.get(chave)), "")
        resultados.append({
            "nome": item.get("display_name", "(sem nome)"),
            "lat": item.get("lat"),
            "lon": item.get("lon"),
            "cc": cc,
            "iso3": iso2_para_iso3(cc),
            "pais": end.get("country", ""),
            "estado": end.get("state", ""),
            "cidade": cidade,
            "osm_tipo": item.get("osm_type", ""),
            "osm_id": item.get("osm_id", ""),
        })
    cache.set(chave, resultados, 3600)
    return resultados


# --------------------------------------------------------------------------
# Climate TRACE
# --------------------------------------------------------------------------
def extrair_emissao(payload, iso3):
    """
    Extrai o total de CO2e (toneladas) da resposta da API, de forma tolerante
    a variações de formato. Retorna float ou None.
    """
    if isinstance(payload, dict):
        for k in ("data", "results", "items", "emissions"):
            if isinstance(payload.get(k), list):
                payload = payload[k]
                break
        else:
            payload = [payload]
    if not isinstance(payload, list):
        return None

    for item in payload:
        if not isinstance(item, dict):
            continue
        pais = item.get("country") or item.get("Country") or item.get("iso3_country")
        if pais and str(pais).upper() != iso3.upper():
            continue
        em = item.get("emissions", item)
        if not isinstance(em, dict):
            continue
        for campo in ("co2e_100yr", "co2e_100yr_total", "co2e_20yr"):
            valor = em.get(campo)
            if isinstance(valor, (int, float)):
                return float(valor)
    return None


def _consultar_ct(iso3, ano, setor=None):
    """Consulta o Climate TRACE. Retorna (total_ou_None, mensagem_de_erro)."""
    chave = ("ct", iso3, ano, setor)
    em_cache = cache.get(chave)
    if em_cache is not None:
        return em_cache

    erros = []
    for base in CLIMATETRACE_BASES:
        params = {"since": ano, "to": ano, "countries": iso3}
        if setor:
            params["sector"] = setor
            params["sectors"] = setor
        try:
            payload = http_get_json(f"{base.rstrip('/')}/country/emissions", params)
        except ErroExterno as e:
            erros.append(str(e))
            continue
        valor = extrair_emissao(payload, iso3)
        if valor is not None:
            resultado = (valor, None)
            cache.set(chave, resultado, 86400)
            return resultado
        erros.append(f"{base}: formato de resposta não reconhecido")
    return (None, " | ".join(erros) or "sem resposta")


def diagnostico_emissoes(iso3, ano):
    """Total do país + divisão por setor (quando a API permitir)."""
    total, erro = _consultar_ct(iso3, ano)
    if total is None:
        return {"ok": False, "erro": erro}

    setores = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futuros = {s: pool.submit(_consultar_ct, iso3, ano, s) for s in SETORES}
        for s, f in futuros.items():
            valor, _ = f.result()
            if valor is not None:
                setores[s] = valor

    aviso = None
    # Proteção: se a API ignorou o filtro de setor, todos os valores seriam
    # iguais ao total. Nesse caso NÃO mostramos a divisão (seria falsa).
    if setores and all(abs(v - total) < 1e-6 * max(total, 1) for v in setores.values()):
        setores = {}
        aviso = "A API não aplicou o filtro por setor; exibindo apenas o total."
    elif not setores:
        aviso = "Divisão por setor indisponível nesta consulta."

    linhas = []
    if setores:
        soma = sum(setores.values()) or 1
        for s, v in sorted(setores.items(), key=lambda x: -x[1]):
            linhas.append({"setor": SETORES[s], "mt": v / 1e6,
                           "pct": 100 * v / soma})
    return {"ok": True, "total_mt": total / 1e6, "setores": linhas, "aviso": aviso}


# --------------------------------------------------------------------------
# Banco de dados (SQLite) - ONGs
# --------------------------------------------------------------------------
ONGS_INICIAIS = [
    ("WWF-Brasil", "Organização de conservação da natureza com atuação em clima, florestas e água.",
     "Clima, Florestas, Biodiversidade", "Brasil", "https://www.wwf.org.br"),
    ("Greenpeace Brasil", "Organização independente que faz campanhas por proteção ambiental e justiça climática.",
     "Clima, Florestas, Oceanos", "Brasil", "https://www.greenpeace.org/brasil/"),
    ("SOS Mata Atlântica", "Atua na defesa e recuperação da Mata Atlântica e monitoramento do bioma.",
     "Mata Atlântica, Restauração florestal", "Mata Atlântica, Brasil", "https://www.sosma.org.br"),
    ("Instituto Socioambiental (ISA)", "Atua em questões socioambientais, com foco em povos indígenas e Amazônia.",
     "Amazônia, Territórios indígenas", "Amazônia, Brasil", "https://www.socioambiental.org"),
    ("Observatório do Clima", "Rede de organizações da sociedade civil sobre mudanças climáticas no Brasil.",
     "Clima, Políticas públicas, Emissões", "Brasil", "https://www.oc.eco.br"),
    ("Projeto TAMAR", "Conservação das tartarugas marinhas e dos ambientes costeiros.",
     "Tartarugas marinhas, Costa", "Litoral do Brasil", "https://www.tamar.org.br"),
    ("Imazon", "Instituto de pesquisa que monitora e propõe soluções para a Amazônia.",
     "Amazônia, Desmatamento", "Amazônia, Brasil", "https://imazon.org.br"),
]


def get_db():
    if "db" not in g:
        from flask import current_app
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(caminho):
    con = sqlite3.connect(caminho)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ongs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT NOT NULL,
            causas TEXT NOT NULL DEFAULT '',
            regiao TEXT NOT NULL DEFAULT '',
            site TEXT NOT NULL DEFAULT '',
            participacao TEXT NOT NULL DEFAULT '',
            verificada INTEGER NOT NULL DEFAULT 0
        )""")
    if con.execute("SELECT COUNT(*) FROM ongs").fetchone()[0] == 0:
        con.executemany(
            "INSERT INTO ongs (nome, descricao, causas, regiao, site) VALUES (?,?,?,?,?)",
            ONGS_INICIAIS)
    con.commit()
    con.close()


def site_valido(url):
    p = urlparse(url) if url else None
    return not url or (p.scheme in ("http", "https") and bool(p.netloc))


def ongs_para_regiao(db, cc, pais, estado, cidade):
    """ONGs cuja região menciona cidade/estado/país, ou é global."""
    termos = [t.lower() for t in (cidade, estado, pais) if t]
    achadas = []
    for ong in db.execute("SELECT * FROM ongs ORDER BY nome"):
        reg = ong["regiao"].lower()
        if (any(t in reg for t in termos) or "global" in reg or "mundial" in reg
                or (cc == "BR" and "brasil" in reg)):
            achadas.append(ong)
    return achadas


# --------------------------------------------------------------------------
# Aplicação
# --------------------------------------------------------------------------
def fmt_num(valor, casas=1):
    """Formato brasileiro: 1.234,5"""
    s = f"{valor:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def create_app(caminho_db=None):
    app = Flask(__name__)
    app.config["DATABASE"] = caminho_db or os.path.join(BASE_DIR, "ecoacao.db")
    app.config["SECRET_KEY"] = os.environ.get("ECOACAO_SECRET", os.urandom(16).hex())
    app.jinja_env.filters["num"] = fmt_num
    init_db(app.config["DATABASE"])

    @app.teardown_appcontext
    def fechar_db(_):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.context_processor
    def globais():
        return {"ANO_MIN": ANO_MIN, "ANO_MAX": ANO_MAX, "ANO_PADRAO": ANO_PADRAO}

    # ---- páginas ----------------------------------------------------------
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/buscar")
    def buscar():
        q = request.args.get("q", "").strip()
        ano = request.args.get("ano", ANO_PADRAO, type=int)
        if not (2 <= len(q) <= 100):
            flash("Digite entre 2 e 100 caracteres.")
            return redirect(url_for("index"))
        ano = min(max(ano, ANO_MIN), ANO_MAX)
        try:
            locais = buscar_locais(q)
        except ErroExterno as e:
            return render_template("erro.html", titulo="Falha na busca de local",
                                   mensagem=str(e)), 502
        return render_template("buscar.html", q=q, ano=ano, locais=locais)

    @app.get("/diagnostico")
    def diagnostico():
        cc = request.args.get("cc", "").strip().upper()
        try:
            ano = int(request.args.get("ano", ANO_PADRAO))
        except ValueError:
            abort(400, "Ano inválido.")
        iso3 = iso2_para_iso3(cc)
        if not re.fullmatch(r"[A-Z]{2}", cc) or not iso3:
            abort(400, "Código de país inválido.")
        if not (ANO_MIN <= ano <= ANO_MAX):
            abort(400, f"Ano deve estar entre {ANO_MIN} e {ANO_MAX}.")
        local = {k: request.args.get(k, "")[:200]
                 for k in ("nome", "pais", "estado", "cidade")}
        local["cc"], local["iso3"] = cc, iso3
        resultado = diagnostico_emissoes(iso3, ano)
        ongs = ongs_para_regiao(get_db(), cc, local["pais"], local["estado"], local["cidade"])
        return render_template("diagnostico.html", local=local, ano=ano,
                               r=resultado, ongs=ongs)

    @app.get("/ongs")
    def ongs():
        q = request.args.get("q", "").strip()[:100]
        db = get_db()
        if q:
            like = f"%{q}%"
            lista = db.execute(
                """SELECT * FROM ongs WHERE nome LIKE ? OR descricao LIKE ?
                   OR causas LIKE ? OR regiao LIKE ? ORDER BY nome""",
                (like, like, like, like)).fetchall()
        else:
            lista = db.execute("SELECT * FROM ongs ORDER BY nome").fetchall()
        return render_template("ongs.html", lista=lista, q=q)

    @app.route("/ongs/nova", methods=["GET", "POST"])
    def ong_nova():
        if request.method == "GET":
            return render_template("ong_form.html", f={}, erros=[])
        f = {k: request.form.get(k, "").strip() for k in
             ("nome", "descricao", "causas", "regiao", "site", "participacao")}
        erros = []
        if not (2 <= len(f["nome"]) <= 120):
            erros.append("Nome: de 2 a 120 caracteres.")
        if not (10 <= len(f["descricao"]) <= 600):
            erros.append("Descrição: de 10 a 600 caracteres.")
        for campo, limite in (("causas", 200), ("regiao", 200), ("participacao", 400)):
            if len(f[campo]) > limite:
                erros.append(f"{campo.capitalize()}: máximo {limite} caracteres.")
        if len(f["site"]) > 300 or not site_valido(f["site"]):
            erros.append("Site: use um endereço http:// ou https:// válido.")
        if erros:
            return render_template("ong_form.html", f=f, erros=erros), 400
        db = get_db()
        try:
            db.execute(
                """INSERT INTO ongs (nome, descricao, causas, regiao, site, participacao)
                   VALUES (?,?,?,?,?,?)""",
                (f["nome"], f["descricao"], f["causas"], f["regiao"], f["site"],
                 f["participacao"]))
            db.commit()
        except sqlite3.IntegrityError:
            return render_template("ong_form.html", f=f,
                                   erros=["Já existe uma ONG com esse nome."]), 409
        flash("ONG cadastrada (marcada como ainda não verificada).")
        return redirect(url_for("ongs"))

    @app.get("/fontes")
    def fontes():
        return render_template("fontes.html")

    @app.get("/debug/climatetrace")
    def debug_ct():
        """Mostra a resposta crua da API para conferir o formato."""
        iso3 = request.args.get("pais", "BRA").upper()
        ano = request.args.get("ano", ANO_PADRAO, type=int)
        saida = []
        for base in CLIMATETRACE_BASES:
            url = f"{base.rstrip('/')}/country/emissions"
            try:
                payload = http_get_json(url, {"since": ano, "to": ano, "countries": iso3})
                texto = repr(payload)[:3000]
                saida.append(f"URL: {url}\nextraído: {extrair_emissao(payload, iso3)}\n{texto}")
            except ErroExterno as e:
                saida.append(f"URL: {url}\nERRO: {e}")
        return "\n\n".join(saida), 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.errorhandler(400)
    def erro_400(e):
        return render_template("erro.html", titulo="Requisição inválida",
                               mensagem=getattr(e, "description", "")), 400

    @app.errorhandler(404)
    def erro_404(e):
        return render_template("erro.html", titulo="Página não encontrada",
                               mensagem="Esse endereço não existe."), 404

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
