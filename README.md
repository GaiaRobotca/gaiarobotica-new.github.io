# GAIA Robótica · UFTM

Site do projeto GAIA, com projetos, equipe, conquistas e guias de robótica.

- Site: https://gaiarobotca.github.io/gaiarobotica-new.github.io/
- Link para a bio: https://gaiarobotca.github.io/gaiarobotica-new.github.io/paginas/portal.html
- Instagram: https://www.instagram.com/gaia.robotica/

## Organização

```text
index.html                Página inicial e equipe
paginas/                  Aprenda, contato, patrocínio, ex-membros e portal
artigos/                  Guias técnicos
noticias/                 Histórias dos projetos
conquistas/               Resultados e galerias
assets/css/site.css       Identidade visual, navegação e componentes gerais
assets/css/articles.css   Componentes compartilhados dos tutoriais
assets/css/stories.css    Leitura das notícias e conquistas
assets/css/pages/         Layouts específicos das páginas
assets/js/site.js         Menu, sumário, leitura, cópia de código e galerias
assets/js/pages/          Busca/filtros e formulários
assets/images/            Imagens por assunto, com nomes e formatos normalizados
data/site.json            Endereço público, títulos e descrições
data/team.json            Integrantes da grade da equipe
data/images.json          Correspondência entre arquivos originais e imagens do site
scripts/                  Sincronização e validação
```

Os pequenos HTML na raiz, como `aprenda.html` e `artigo-pid.html`, preservam os endereços antigos e redirecionam para as páginas organizadas. Edite o conteúdo nas pastas, não nesses redirecionamentos. `index.html` continua sendo a entrada do site.

## Editar e visualizar

Não há dependência de um framework ou servidor de aplicação. O conteúdo e a navegação são HTML estático.

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Abra http://127.0.0.1:8765/. Não use `file://` para testar recursos de área de transferência.

1. Edite o HTML da página e, se necessário, seu CSS em `assets/css/pages/`.
2. Para o cabeçalho/rodapé compartilhados, edite os modelos em `scripts/sync_site.py`.
3. Para títulos de compartilhamento, descrições e endereço público, edite `data/site.json`.
4. Execute `python scripts/sync_site.py` para atualizar componentes compartilhados, metadados, sitemap e redirecionamentos.
5. Execute `python scripts/validate_site.py` antes de enviar as alterações.

Os blocos delimitados por `shared-header`, `shared-footer`, `page-meta` e `team-members` são gerados pelo script. A execução preserva todo o conteúdo fora desses blocos.

## Atualizar a equipe

Adicione o retrato em `assets/images/equipe/`, preferencialmente WebP, com nome sem espaços ou acentos. Atualize nome, função e caminho em `data/team.json` e execute `python scripts/sync_site.py`.

Um integrante com `"photo": null` recebe suas iniciais; não há imagens externas de substituição. Para retirar alguém da grade atual, altere `status` e registre a pessoa em `paginas/ex-membros.html`. Liderança e docentes ficam no bloco próprio de `index.html`.

Na reorganização, foram mantidos os integrantes já publicados e vinculadas as 12 fotos da pasta `Equipe Gaia`. A ausência de retrato não foi tratada como saída da equipe. O post de referência do Instagram não pôde ser consultado automaticamente; mudanças adicionais de nomes, funções e status precisam de confirmação do capitão.

## Fotos

Os arquivos com extensão JPG/PNG que continham HEIC foram convertidos. Imagens repetidas compartilham o mesmo arquivo; `data/images.json` registra a correspondência, o formato original e o hash. Fotos de pessoas não foram substituídas por imagens geradas.

Os originais foram preservados fora da pasta publicada, em `../gaia-midias-originais-20260919/`, além do backup ZIP criado antes da reorganização. As versões anteriores também ficam no histórico Git. Para inserir novas imagens, exporte no formato real indicado pela extensão e confira os nomes com diferenciação entre maiúsculas e minúsculas: o GitHub Pages usa caminhos sensíveis a isso.

## Contato e patrocínio

Os formulários preparam uma mensagem no aplicativo de e-mail ou copiam o texto. **O visitante ainda precisa enviar o e-mail.** Não há serviço de envio ou armazenamento de mensagens no site. A interface explica esse comportamento e mantém os canais diretos de contato.

## Validação

O validador estático usa apenas a biblioteca padrão do Python e verifica caminhos, maiúsculas/minúsculas, âncoras, IDs, imagens e estrutura das páginas. Não confirma a disponibilidade de links externos.

Para repetir os testes no navegador, instale as ferramentas em um ambiente virtual:

```sh
python -m venv .venv
# Ative o ambiente conforme seu sistema operacional.
python -m pip install playwright
python -m playwright install chromium
python scripts/check_browser.py
```

Mantenha o servidor local na porta 8765 em outro terminal. O teste cobre as 22 páginas em quatro larguras, menu mobile, imagens, busca, rascunhos, galerias e redirecionamentos. Os rascunhos são testados localmente; nenhuma mensagem é enviada. Capturas e relatório são salvos na pasta temporária do sistema.

## Publicação

O GitHub Pages deste repositório publica a raiz da branch `main`. Depois de validar, envie o commit e acompanhe a execução de `pages build and deployment` no GitHub Actions. Confira o site publicado antes de divulgar o link do portal na bio.

Fontes das correções históricas, como o resultado da SAE em junho de 2025 e o HackaGIS Saúde, estão vinculadas nos próprios relatos.
