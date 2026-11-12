"""Testes offline (a internet é simulada). Rode: python -m unittest -v"""
import os
import tempfile
import unittest
from unittest import mock

import app as ecoacao
from iso_countries import ISO2_TO_ISO3, iso2_para_iso3

NOMINATIM_FAKE = [{
    "display_name": "Itajaí, Santa Catarina, Brasil", "lat": "-26.9", "lon": "-48.6",
    "osm_type": "relation", "osm_id": 1,
    "address": {"city": "Itajaí", "state": "Santa Catarina",
                "country": "Brasil", "country_code": "br"},
}]


def api_fake(url, params=None):
    if "nominatim" in url:
        return NOMINATIM_FAKE
    setor = (params or {}).get("sector")
    valores = {None: 1000e6, "power": 100e6, "transportation": 300e6,
               "agriculture": 600e6}
    if setor and setor not in valores:
        raise ecoacao.ErroExterno("sem dados")
    return [{"country": "BRA", "emissions": {"co2e_100yr": valores[setor]}}]


class Testes(unittest.TestCase):
    def setUp(self):
        ecoacao.cache._dados.clear()
        fd, self.db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.remove(self.db)
        self.app = ecoacao.create_app(self.db)
        self.c = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db):
            os.remove(self.db)

    def test_iso(self):
        self.assertGreaterEqual(len(ISO2_TO_ISO3), 249)
        self.assertEqual(len(set(ISO2_TO_ISO3.values())), len(ISO2_TO_ISO3))
        self.assertTrue(all(len(v) == 3 for v in ISO2_TO_ISO3.values()))
        self.assertEqual(iso2_para_iso3("br"), "BRA")
        self.assertIsNone(iso2_para_iso3("zz"))

    def test_paginas_basicas(self):
        for rota in ("/", "/ongs", "/ongs/nova", "/fontes"):
            self.assertEqual(self.c.get(rota).status_code, 200, rota)
        self.assertEqual(self.c.get("/naoexiste").status_code, 404)

    def test_ongs_seed_e_filtro(self):
        self.assertIn("WWF-Brasil", self.c.get("/ongs").get_data(as_text=True))
        r = self.c.get("/ongs?q=tartaruga").get_data(as_text=True)
        self.assertIn("TAMAR", r)
        self.assertNotIn("WWF-Brasil", r)

    def test_sql_injection_no_filtro(self):
        r = self.c.get("/ongs?q=' OR 1=1 --")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Nenhuma ONG", r.get_data(as_text=True))

    def test_cadastro_ong(self):
        dados = {"nome": "ONG Teste", "descricao": "Descrição com tamanho ok.",
                 "site": "https://exemplo.org", "regiao": "Itajaí"}
        r = self.c.post("/ongs/nova", data=dados)
        self.assertEqual(r.status_code, 302)
        self.assertIn("ONG Teste", self.c.get("/ongs").get_data(as_text=True))
        # duplicada
        self.assertEqual(self.c.post("/ongs/nova", data=dados).status_code, 409)

    def test_cadastro_validacoes(self):
        base = {"nome": "X Y", "descricao": "Descrição com tamanho ok."}
        self.assertEqual(self.c.post("/ongs/nova", data={**base, "site": "javascript:alert(1)"}).status_code, 400)
        self.assertEqual(self.c.post("/ongs/nova", data={"nome": "", "descricao": "curta"}).status_code, 400)

    def test_xss_escapado(self):
        self.c.post("/ongs/nova", data={"nome": "<script>alert(1)</script>",
                                        "descricao": "Descrição com tamanho ok."})
        html = self.c.get("/ongs").get_data(as_text=True)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    @mock.patch("app.time.sleep")
    @mock.patch("app.http_get_json", side_effect=api_fake)
    def test_busca(self, _h, _s):
        r = self.c.get("/buscar?q=Itajaí&ano=2023")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("Itajaí", html)
        self.assertIn("/diagnostico?cc=BR", html)

    def test_busca_invalida(self):
        self.assertEqual(self.c.get("/buscar?q=a").status_code, 302)

    @mock.patch("app.time.sleep")
    @mock.patch("app.http_get_json", side_effect=ecoacao.ErroExterno("fora do ar"))
    def test_busca_api_fora(self, _h, _s):
        self.assertEqual(self.c.get("/buscar?q=Itajaí").status_code, 502)

    @mock.patch("app.http_get_json", side_effect=api_fake)
    def test_diagnostico_ok(self, _h):
        r = self.c.get("/diagnostico?cc=BR&ano=2023&pais=Brasil&estado=Santa Catarina&cidade=Itajaí&nome=Itajaí")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("1.000,0", html)          # total em Mt, formato BR
        self.assertIn("Agropecuária", html)
        self.assertIn("60,0%", html)            # 600/1000 dos setores
        self.assertIn("TAMAR", html)            # ONG regional

    @mock.patch("app.http_get_json",
                return_value=[{"country": "BRA", "emissions": {"co2e_100yr": 5e8}}])
    def test_api_ignora_filtro_de_setor(self, _h):
        html = self.c.get("/diagnostico?cc=BR&ano=2023").get_data(as_text=True)
        self.assertIn("não aplicou o filtro", html)
        self.assertNotIn("Agropecuária", html)

    @mock.patch("app.http_get_json", side_effect=ecoacao.ErroExterno("HTTP 503"))
    def test_diagnostico_api_fora(self, _h):
        r = self.c.get("/diagnostico?cc=BR&ano=2023")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Não foi possível obter", r.get_data(as_text=True))

    def test_diagnostico_parametros_ruins(self):
        for qs in ("cc=ZZ", "cc=", "cc=BR&ano=1900", "cc=BR&ano=abc", "cc=<b>"):
            self.assertEqual(self.c.get("/diagnostico?" + qs).status_code, 400, qs)

    def test_parser(self):
        f = ecoacao.extrair_emissao
        self.assertEqual(f([{"country": "BRA", "emissions": {"co2e_100yr": 7}}], "BRA"), 7.0)
        self.assertEqual(f({"data": [{"country": "BRA", "co2e_100yr": 3}]}, "BRA"), 3.0)
        self.assertIsNone(f([{"country": "ARG", "emissions": {"co2e_100yr": 7}}], "BRA"))
        self.assertIsNone(f("lixo", "BRA"))
        self.assertIsNone(f([], "BRA"))

    def test_formato_numero(self):
        self.assertEqual(ecoacao.fmt_num(1234.56), "1.234,6")


if __name__ == "__main__":
    unittest.main()
