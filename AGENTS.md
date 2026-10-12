# Instrucoes do projeto

Site estatico GAIA: dados em data/, templates e scripts/sync_site.py. Editar a fonte dos blocos compartilhados e regenerar. Verificar diferencas entre fork pessoal e original; nao substituir um pelo outro.

Ler README e docs antes de alterar. Preservar arquitetura, dados brutos e
autoria/licencas dos materiais externos. Nao inventar hardware, medidas ou
resultados. Marcar UNKNOWN/NOT_MEASURED e separar SIMULATED de REAL.
Fazer mudancas pequenas, com regressao para defeitos corrigidos.

Validacao: `python scripts/validate_site.py`; `python scripts/sync_site.py` seguido de `git diff` para revisar gerados; `node --check` nos JS.

Definition of Done: verificacoes pertinentes, documentacao das alteracoes,
comandos reproduziveis e limites de validacao. Inspecao estatica nao comprova
funcionamento fisico. Ver docs/engineering-status.md para prioridades e estudo.
