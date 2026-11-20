# Crazy Eyes — mostrador

## Escopo decidido
O usuário pediu transformar Crazy Eyes em um mostrador e especificou “números acima dos olhos da mesma forma que está no Aquaticks”. A proposta já apresentada inclui olhos pela inclinação, reação ao toque e modo sempre ativo econômico. A app permanece disponível para o gesto de arrastar, que pertence ao sistema na superfície de mostrador.

A referência Aquaticks usa `androidx.wear.compose.material3.TimeText()` no topo: hora pequena e centralizada em arco, seguindo a borda superior. Reproduzir essa disposição, com 12/24h conforme configuração do relógio e sem segundos. Não usar números grandes abaixo dos olhos.

## Arquitetura e alternativas
Criar módulo Android `watchface`, APK separado `com.luisfelipe.crazyeyes.watchface`, com Watch Face Format 1 e minSdk33 (Wear OS4+). Essa é a abordagem compatível com o formato atual e com a inclinação/toque necessários. Converter a Activity em serviço de mostrador legado prejudicaria compatibilidade atual; substituir a app removeria o arrastar. Ambos descartados.

## Comportamento
- Fundo preto e mesmos olhos grandes da app, com região superior livre para hora em arco.
- Pupilas usam Gyro com deslocamento limitado; quando ACCELEROMETER_IS_SUPPORTED é falso, olham para posições pseudoaleatórias, mudando a cada 2 segundos com transição suave. No WFF não é possível reproduzir o temporizador de sensor obsoleto da Activity.
- Uma máscara animada por olho contrai o olho tocado e abre novamente em cerca de 0,9s. A máscara também recorta a pupila, evitando que ela escape do olho fechado. É adaptação da reação da app, sem prometer vibração no mostrador.
- Piscada leve periódica no modo interativo. Arrastar continua sendo gesto do sistema.
- AOD: hora e contornos estáticos cinza, sem pupilas animadas, com menos de 15% dos pixels acesos.
- Sem complicações, permissões, rede, código executável no APK do mostrador ou serviços próprios. Imagens pré-calculadas e XML; runtime do Wear OS gerencia ciclo de vida.

## Verificação e limites
Validar XML contra o schema oficial WFF1, todos os recursos e a geometria das animações; verificar orçamento de pixels AOD e memória de imagens. Compilar/lint do novo APK e executar suite existente da app. Inspecionar imagens de prévia geradas a partir da definição e verificar manifesto/APK sem classes.dex.

O dispositivo real é necessário para confirmar acionamento do TAP em máscara animada, comportamento do Gyro, seleção do mostrador, AOD e persistência após reiniciar. Não fazer merge sem teste humano.
