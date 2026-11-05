# Manutencao rastreavel do site

Este repositorio e o portal-gaia tem finalidades distintas: site institucional
estatico versus aplicacao conectada ao Firebase. Nao transferir configuracoes,
usuarios ou dados entre eles. O fork pessoal e o repositorio GaiaRobotca
podem divergir; registrar o commit de origem de cada contribuicao.

Para alterar blocos comuns, editar dados/templates usados por sync_site.py,
regenerar e revisar o diff. Executar validate_site.py e verificacao de sintaxe
JavaScript. Esses checks cobrem estrutura, links locais e geracao; nao
substituem revisao visual responsiva, acessibilidade ou links externos.

ALTO: manter origem/autorizacao de fotos, nomes e resultados de competicao;
MEDIO: testar teclado, foco, contraste e navegacao em celular; BAIXO:
medir tamanho dos recursos e carregamento antes de otimizar. Desempenho e
acessibilidade medidos nesta revisao: NOT_MEASURED.

Registro de contribuicao: problema, pagina, fonte alterada, gerados,
comandos/resultados, capturas quando houver mudanca visual e commit.
Nao atribuir todo o site a uma pessoa sem historico que sustente a afirmacao.

Para entender esta implementacao: estude geracao estatica, fonte versus
artefato e caminhos relativos. Desafio: altere um bloco compartilhado numa
branch e confirme que o gerador produz o mesmo resultado na segunda execucao.

## Revisão visual de 05/11/2026

Rebranding a partir de 7d986ff: tokens institucionais, rosto vetorial, ícones,
metadados e loja integrados ao gerador. Evidências, comandos, cobertura e limites
em [Identidade visual](visual-identity.md). A auditoria automática WCAG A/AA com
axe/Chromium cobre 27 contextos página/tema; não certifica conformidade integral
nem substitui testes em dispositivos físicos. Desempenho: NOT_MEASURED.
