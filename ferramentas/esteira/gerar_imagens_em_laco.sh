#!/bin/bash
# Repete gerar_imagens.py --uma-vez até não faltar nenhuma imagem (máx. 5 rodadas).
cd /home/matheuso/workspace/orquestrando_agentes/livro
for i in 1 2 3 4 5; do
  echo "=== rodada $i ($(date +%H:%M:%S))"
  python3 ferramentas/gerar_imagens.py --uma-vez
  python3 - <<'PY' || break
import json, sys
from pathlib import Path
falta=[i['arquivo'] for i in json.load(open('ferramentas/imagens.json'))['imagens'] if not Path(i['arquivo']).exists()]
print('pendentes:', len(falta), falta)
sys.exit(1 if not falta else 0)
PY
done
echo "=== FIM DO LAÇO ($(date +%H:%M:%S))"
