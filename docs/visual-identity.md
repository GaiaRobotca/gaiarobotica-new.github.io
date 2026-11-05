# Identidade visual GAIA — revisão de 05/11/2026

Origem: `GaiaRobotca/gaiarobotica-new.github.io`, base `7d986ff`.
Escopo: 25 páginas em `data/site.json`, 21 redirecionamentos e a loja independente.
Informações, fotografias, autoria, catálogo e fluxos de contato foram preservados.

## Referência e assets

A tarefa disponibilizou apenas o texto. A referência provisória é a imagem histórica
`assets/images/marca/logo-gaia.png`, já presente no repositório: rosto feminino,
cabelos, circuitos e contorno circular. A imagem original permanece intacta.
`scripts/build_brand.py` vetoriza seus contornos, elimina fragmentos menores que
24 px² e aproxima os contornos com tolerância de 1,25 px na resolução original.
Os SVGs são paths vetoriais, sem imagens raster embutidas ou fontes externas.

- `gaia-symbol-dark.svg` / `gaia-symbol-light.svg`: rosto para fundos escuros/claros.
- `gaia-logo-dark.svg` / `gaia-logo-light.svg`: rosto e lettering geométrico GAIA em paths.
  O lettering é uma adaptação provisória; não representa recuperação exata da tipografia original.
- `gaia-favicon.svg`: desenho óptico simplificado, mantendo cabelos, olho fechado,
  contorno facial e circuito na têmpora; sem texto. Não é um novo monograma.
- `gaia-favicon-{16,32,192,512}.png`, `gaia-touch-180.png`, `gaia-favicon.ico`.
- `assets/images/social/gaia-preview{,-horizontal}.{svg,png}`: 2400 × 2400 e 2400 × 1260.

Os cabeçalhos usam o rosto e o nome GAIA em texto acessível, preservando a assinatura
institucional e a navegação. A loja usa a mesma origem de assets, inclusive nas
ilustrações montadas pelo JavaScript. O favicon é a versão com menos detalhes;
o cabeçalho conserva mais traços da referência histórica. Arquivos G antigos
permanecem no histórico/árvore como acervo, sem referências visuais ativas nos HTML/JS.

## Regras de cor e componentes

`assets/css/tokens.css` define a fonte central da paleta:

| Papel | Cor |
| --- | --- |
| Azul institucional / hero / marca | `#001A7F` |
| Verde institucional / ações | `#007A3F` |
| Fundo profundo / navegação / rodapé | `#01195D` |
| Bordas e separadores | `#7F87B4` |
| Texto claro / fundo claro da loja | `#FFF5E9` |
| Destaques e foco sobre fundo escuro | `#C7DC90` |

Tokens semânticos separam ações, texto, foco, links, superfícies e bordas.
Variáveis históricas continuam disponíveis por aliases. As notícias/conquistas
e os temas da loja também mapeiam seus tokens para essa fonte. Texto branco
sobre verde institucional tem contraste aproximado de 5,44:1; creme sobre azul
institucional, 13,4:1. Fundos de links e botões são tratados separadamente da cor
de texto de links. Diagramas, sintaxe de código, alertas, fotografias e logos de
parceiros conservam cores com significado próprio.

Botões principais usam verde e texto branco, com borda clara sobre azul.
Hover usa verde mais escuro. Foco visível usa verde suave no escuro e azul no
tema claro da loja. Gradientes são discretos entre os dois azuis principais.
Menus, grades, formulários e breakpoints existentes foram mantidos.

## Geração e reprodução

O site continua estático, sem dependências novas em produção.
Para recriar os assets, use um ambiente de autoria separado:

```sh
python -m pip install opencv-python-headless playwright pillow
python -m playwright install chromium
python scripts/build_brand.py
python scripts/sync_site.py
python scripts/validate_site.py
node --check assets/js/site.js
node --check loja/js/theme.js
node --check loja/js/store.js
python -m http.server 8765 --bind 127.0.0.1
# Em outro terminal:
python scripts/check_browser.py
```

`build_brand.py` usa o SVG óptico do favicon e o lettering vetorial como mestres
editáveis; não recupera esses desenhos se forem apagados. A vetorização principal
sempre parte do original preservado. A sincronização mantém os ícones, metadados,
assets sociais e redirecionamentos, incluindo o bloco `shop-meta` da loja.

A auditoria adicional usa Chromium e uma cópia local de axe-core:

```sh
npm install --prefix ../brand-tools axe-core
python scripts/check_brand.py --axe-script ../brand-tools/node_modules/axe-core/axe.min.js
```

Esse teste serve o site sob `/gaiarobotica-new.github.io/`, verifica as 25 páginas
e a loja nos dois temas, audita regras WCAG A/AA disponíveis no axe, verifica
overflow em 320/390/768/1440 px e exercita tema persistido, filtro, sacola,
quantidade, persistência e preparação do pedido. O clique `mailto:` é bloqueado
no teste; nenhuma mensagem é enviada.

## Evidências e limites

- Sincronização e validação estática: 47 HTML, 1387 referências, zero erros.
- Segunda sincronização: nenhum HTML alterado por comparação SHA-256.
- Chromium: 100 verificações de layout das 25 páginas, sem falhas de imagem,
  overflow ou JavaScript; sete verificações de interação aprovadas.
- Auditoria adicional: 27 contextos de página/tema, 108 verificações de overflow,
  nenhum erro HTTP local e nenhuma violação automática WCAG A/AA detectada.
- Capturas antes/depois: home, portal, Aprenda, Contato e loja nos dois temas,
  em quatro larguras. Evidências de entrega ficam fora da árvore publicada.

O teste antigo de Aprenda esperava oito cards, enquanto o catálogo publicado já
continha dez. Ele agora compara o resultado com todos os cards e verifica também
o pertencimento à categoria, preservando a capacidade de detectar filtros incorretos.

Uma execução concorrente registrou falha transitória de decodificação na logo
inalterada de um parceiro. O JPEG foi verificado e a repetição completa isolada
terminou com 107 verificações e zero falhas; o asset não foi modificado.

Validação automática não certifica conformidade WCAG integral. Firefox, Edge,
Safari, dispositivos físicos, cache de compartilhamento e publicação em produção
não foram testados. A identidade permanece provisória até comparação com o novo
arquivo oficial mencionado na tarefa. Não houve merge nem mudança na branch main.
