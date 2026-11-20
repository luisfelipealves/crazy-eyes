# Crazy Eyes — app para Wear OS

## Intenção e decisão
O usuário pediu dois olhos que respondem ao acelerômetro, olham em direções aleatórias na ausência dele, seguem o dedo arrastado e reagem comicamente a uma cutucada por toque rápido. Após comparar app e mostrador, escolheu: “Siga como app”. A instrução autoriza executar a proposta já apresentada, sem novas rodadas de perguntas.

## Abordagens
- App nativa (escolhida): permite gestos de arrastar e animação arbitrária.
- Mostrador WFF: permite inclinação e animação por toque, mas não o arrastar livre necessário. Descartado para esta entrega.

## Escopo
- Kotlin, Canvas Android, tela preta, olhos brancos grandes e pupilas escuras, sem menus.
- Wear OS 3+ (minSdk 30), compile/target 36; aplicação independente, offline, sem permissões de rede ou saúde, sem backend.
- Sensor de gravidade preferido para inclinação estável, acelerômetro como segunda opção. Se o sensor estiver ausente, falhar ao registrar ou ficar 2 segundos sem dados válidos, olhar aleatório suave com pausas. Retomar sensor quando voltarem os dados.
- Coordenadas do sensor adaptadas à rotação da tela. Limitar deslocamento das pupilas ao contorno dos olhos.
- Enquanto há um dedo na tela, ele domina o olhar; cada olho olha em direção ao dedo, produzindo convergência. Arrastar nunca causa cutucada.
- Toque de até 250 ms, sem ultrapassar o touch slop do Android, cutuca o olho atingido: fecha, contrai, fica brevemente rosado e recupera em 900 ms; o outro arregala. Toque fora dos olhos provoca uma piscada. Vibração curta usando feedback de toque do sistema.
- Piscadas ocasionais e recuperação suave ao soltar o dedo. Toque cancelado ou segundo dedo não produzem cutucada indevida.
- Suspender sensores e redesenho quando a app perde foco, pausa ou a tela apaga. Não manter a tela ligada artificialmente.

## Escolhas de implementação
O desenvolvedor escolheu View/Canvas para reduzir dependências, desenho vetorial para escalar em telas redondas e estado de animação puro Kotlin para testar tempo, sensores e gestos. A aparência e os tempos acima são padrões escolhidos pelo desenvolvedor, ajustáveis após teste no relógio.

## Verificação
Testes JVM do motor (prioridade, limites, aleatoriedade, sensor obsoleto, rotação, toque e cancelamento), integração Android via Robolectric (entrada e ciclo de vida), lint e APK debug compilado. Renderizar imagens do Canvas para revisão visual. Teste humano final no Galaxy Watch 5 Pro; não fazer merge antes dele.

## Fora do escopo
Mostrador, complication, Tile, serviço em segundo plano, configurações, som, nuvem e publicação na Play Store.
