"""Monta o bloco de bancos do index.html a partir das planilhas e das anotacoes.
Anotacoes (dicas.tsv): id <TAB> niveis <TAB> dificuldade <TAB> dica
  id: x<num> para gerais, y<num> para area, z<num> para estatistica
  niveis: letras de t (TCC), e (especializacao), m (mestrado), d (doutorado)
  dificuldade: 1, 2 ou 3
Uso: python3 dados/montar_bancos.py"""
import csv, json, os, re
D = os.path.dirname(os.path.abspath(__file__))
g = list(csv.DictReader(open(D+'/perguntas_gerais.csv', encoding='utf-8-sig'), delimiter=';'))
s = list(csv.DictReader(open(D+'/perguntas_area.csv', encoding='utf-8-sig'), delimiter=';'))
an = {}
if os.path.exists(D+'/dicas.tsv'):
    for ln in open(D+'/dicas.tsv', encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln or ln.startswith('#'): continue
        i, niv, n, dica = ln.split('\t')
        assert re.fullmatch(r'[temd]+', niv) and n in '123', ln
        assert not re.search('[—–]|nortear|capacitad', dica, re.I), ln
        an[i] = [niv, int(n), dica]
gen = []
for r in g:
    if r['modalidade'] != 'direta': continue
    i = 'x'+r['id']; a = an.get(i)
    gen.append([int(r['id']), r['categoria'], r['pergunta']] + (a if a else []))
t = list(csv.DictReader(open(D+'/perguntas_estatistica.csv', encoding='utf-8-sig'), delimiter=';'))
est = []
for r in t:
    i = 'z'+r['id']; a = an.get(i)
    est.append([int(r['id']), r['categoria'].replace(' — ', ': ').strip(), r['pergunta']] + (a if a else []))
esp = {}
for r in s:
    i = 'y'+r['id']; a = an.get(i)
    esp.setdefault(r['area'], {}).setdefault(r['categoria'], []).append([int(r['id']), r['pergunta']] + (a if a else []))
js = "/* BANCOS-INICIO (gerado por dados/montar_bancos.py) */\n"
js += "const GEN = "+json.dumps(gen, ensure_ascii=False, separators=(',',':'))+";\n"
js += "const EST = "+json.dumps(est, ensure_ascii=False, separators=(',',':'))+";\n"
js += "const ESP = "+json.dumps(esp, ensure_ascii=False, separators=(',',':'))+";\n"
js += 'const REPLICAS = ["Que razões sustentam a sua resposta?","Você pode ilustrar com um exemplo do seu trabalho?","Que ressalva você faria à sua própria resposta?"];\n'
js += "/* BANCOS-FIM */\n"
p = os.path.join(D, '..', 'index.html'); h = open(p, encoding='utf-8').read()
i, j = h.index('/* BANCOS-INICIO'), h.index('/* BANCOS-FIM */')+len('/* BANCOS-FIM */\n')
open(p, 'w', encoding='utf-8').write(h[:i]+js+h[j:])
fg = sum(1 for x in gen if len(x) > 3); fe = sum(1 for v in esp.values() for c in v.values() for x in c if len(x) > 2)
ft = sum(1 for x in est if len(x) > 3)
print(f"gerais com dica: {fg}/{len(gen)} | area com dica: {fe}/1000 | estatistica com dica: {ft}/{len(est)}")
