# Verificação — Crazy Eyes 0.1.0

## Evidência local
- 19 testes: 12 de motor, 5 de integração/desenho, 2 de sensores; 0 falhas.
- `testDebugUnitTest lintDebug assembleDebug`: sucesso com Gradle 8.13, JDK17, SDK36.
- Integração Robolectric executada em SDK35; minSdk30 conferido no código, sem teste de runtime em API30 nesta entrega.
- Lint: 0 erros, 5 avisos (constante de receiver API33, metadados de recents Wear OS, construtor Java da View, regras de extração de backup e atualização disponível de Robolectric). Sem bloqueador identificado na revisão independente.
- Renderização de produção inspecionada nos estados normal, inclinado, seguindo dedo e cutucado.
- Certificado debug SHA256: `88cf8e4b5bedc4f98e72cc4e56fb3f42b2942e25d206eac2d84c94ae55d14e44`.

## Revisão independente
Nenhum problema crítico ou importante identificado. Observação menor adiada: ampliar o teste do ciclo de vida para afirmar conjuntamente a interrupção de redesenho e a liberação de sensores pela Activity. A implementação foi inspecionada e esses recursos são liberados.

## Pendências
Teste real no Galaxy Watch 5 Pro: direção e sensibilidade do sensor, vibração, navegação, tela apagada/retomada e consumo de bateria. Ver [HUMAN_TESTING.md](HUMAN_TESTING.md). Merge somente após aprovação do usuário nesse teste.

O workflow GitHub Actions replica os comandos locais; seu resultado remoto deve ser consultado na PR.
