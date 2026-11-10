# Crazy Eyes Face — teste no relógio

## Versão 0.1.7-experimental — expressões automáticas

- Bateria em20% ou menos, fora do carregador: pálpebras baixam, deixando os olhos cansados.
- Carregando: olhos abertos e íris pulsando suavemente, mesmo com bateria baixa. A carga tem prioridade.
- Ao desconectar com20% ou menos, voltam a ficar cansados; acima de20%, voltam ao normal.
- Os quatro estilos, seis cores, hora, toque, inclinação, sacudida e modo sempre ligado continuam disponíveis. As expressões não alteram a tela ambiente.
- Instalar `crazy-eyes-shake-0.1.7-debug.apk`; se houver conflito de assinatura, desinstalar a versão de teste anterior.
- [ ] No carregador, abrir o mostrador e conferir a pulsação das duas íris.
- [ ] Com bateria baixa, conferir as pálpebras nos estilos favoritos e a reação ao toque.

## Versão 0.1.6-experimental — correção do fundo retangular

As máscaras do formato e da animação agora são aplicadas em grupos separados. Isso evita que a máscara retangular do piscar amplie o recorte do olho e esconda o estilo. Os IDs, estilos, cores e gestos continuam os mesmos.

- Instalar `crazy-eyes-shake-0.1.6-debug.apk`; desinstalar a versão de teste anterior em caso de conflito de assinatura.
- [ ] Alternar Cartoon, Gato, Robô e Monstrinho: conferir o formato completo com os olhos abertos, sem retângulos cobrindo o desenho.
- [ ] Tocar em cada olho: a abertura fecha e volta ao mesmo formato; moldura e outro olho permanecem.
- [ ] Conferir a escolha após apagar/acender a tela e reiniciar.

## Versão 0.1.5-experimental — estilos do olho inteiro

Correção do escopo: o estilo agora troca o formato, a parte branca, a moldura/pálpebra e a pupila dos dois olhos. Cartoon mantém os ovais; Gato usa aberturas amendoadas com pontas e pupilas verticais; Robô usa olhos quadrados, moldura metálica e sensores quadrados; Monstrinho usa contornos verdes irregulares e pálpebras grossas.

- Instalar `crazy-eyes-shake-0.1.5-debug.apk`; se houver conflito de assinatura, desinstalar a versão de teste anterior.
- Em **Personalizar/Editar**, alternar os quatro estilos e as seis cores. A cor continua alterando apenas a íris, sem recolorir a moldura.
- [ ] Conferir a mudança do contorno completo, incluindo Robô e Monstrinho, e verificar os mesmos formatos no modo sempre ligado.
- [ ] Tocar em cada olho separadamente: apenas sua abertura fecha; moldura e outro olho permanecem.
- [ ] Inclinar e sacudir: pupilas acompanham o movimento e ficam recortadas pelas pálpebras/molduras.
- [ ] Confirmar a seleção depois de sair do editor, apagar/acender a tela e reiniciar.

## Versão 0.1.4-experimental — personalização

- Instalar `crazy-eyes-shake-0.1.4-debug.apk`. Se houver conflito de assinatura, desinstalar o Crazy Eyes Shake anterior primeiro.
- Selecionar **Crazy Eyes Shake**, manter pressionado no mostrador e abrir **Personalizar/Editar** (ou usar o editor do Galaxy Wearable).
- **Estilo dos olhos:** Cartoon, Gato, Robô e Monstrinho.
- **Cor da íris:** Cinza, Azul, Verde, Castanho, Roxo e Âmbar. Ambas as escolhas são independentes e se aplicam aos dois olhos. Padrão: Cartoon/Cinza.
- [ ] Alterar estilo e cor, salvar e confirmar que a seleção permanece depois de sair do editor, apagar/acender a tela e reiniciar o relógio.
- [ ] Conferir que hora, inclinação invertida, sacudida ampla e reação ao toque continuam funcionando em cada estilo.
- [ ] Conferir que o modo sempre ligado mantém hora e contornos discretos, sem as íris coloridas.

## Versão 0.1.3-experimental

- Giro da sacudida com raio 26 (antes 14), aproximadamente 86% mais amplo.
- Pivô abaixo do centro da pupila para aproveitar a altura do olho. Posição neutra preservada; pupilas giram em sentidos opostos e retornam após aproximadamente 3 segundos.
- Fonte 40 e direção invertida do acelerômetro mantidas.
- Instalar `crazy-eyes-shake-0.1.3-debug.apk` e selecionar **Crazy Eyes Shake**. Desinstalar o APK de teste anterior se houver conflito de assinatura.
- No relógio, comparar a amplitude, repetir a sacudida e verificar toque e retorno à inclinação normal.

## Versão 0.1.2-experimental

- Hora em arco acima dos olhos com fonte 40 (antes 26), em 12h/24h e AOD.
- Direção do acelerômetro invertida em X e Y: uma mesma inclinação move as pupilas para o lado oposto ao da versão anterior; os eixos não foram trocados entre si.
- Instalar `crazy-eyes-shake-0.1.2-debug.apk` e selecionar **Crazy Eyes Shake**. APKs de teste podem usar certificados diferentes; se o Android acusar conflito de assinatura, desinstalar o Crazy Eyes Shake anterior antes de instalar.

## Experimento de sacudida (0.1.1-experimental)

O pacote `com.luisfelipe.crazyeyes.watchface.shake`, nome **Crazy Eyes Shake**, é separado do mostrador já validado. O experimento testa uma transição angular WFF de 3 segundos depois de uma aceleração forte (módulo acima de 25 m/s²). Não é um detector de padrão de sacudida com histórico; uma pancada ou outro movimento forte também pode disparar.

Instale `crazy-eyes-shake-0.1.1-debug.apk` pelo mesmo instalador usado antes e selecione **Adicionar mostrador → Crazy Eyes Shake**. Pelo computador, use `adb install -r crazy-eyes-shake-0.1.1-debug.apk`; para ativar diretamente:

```sh
adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId com.luisfelipe.crazyeyes.watchface.shake
```

As instruções abaixo, com **Crazy Eyes Face**, referem-se à versão estável, não a este experimento.

- [ ] Sacudir com a tela ativa produz giro horário à esquerda e anti-horário à direita.
- [ ] O giro continua depois de parar o pulso e termina em aproximadamente 3 segundos.
- [ ] Outra sacudida, depois de parar, funciona novamente.
- [ ] Inclinar devagar ou deixar parado não dispara o efeito.
- [ ] Hora, toque e AOD continuam como antes.

O teste `python -m tools.watchface_device_check --package com.luisfelipe.crazyeyes.watchface.shake` usa o renderer do emulador, registra capturas e mede as pupilas após soltar o sensor. A prévia Python não simula a duração de animações. A sensibilidade em pulso real e a bateria exigem teste físico. Não considerar o experimento validado apenas por passar no schema.

APK separado da app Crazy Eyes. Requer Wear OS 4 ou superior (API33+).

## Instalação
Com o relógio e computador na mesma rede, ative a depuração sem fio e use:

```sh
adb pair IP:PORTA_DE_PAREAMENTO
adb connect IP:PORTA_DE_DEPURACAO
adb install -r crazy-eyes-face-0.1.0-debug.apk
```
Depois pressione o mostrador atual por alguns segundos, escolha **Adicionar mostrador** e selecione **Crazy Eyes Face**. Ele aparece na seleção de mostradores, não no menu de apps.

Opcional para desenvolvimento, após instalar:

```sh
adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId com.luisfelipe.crazyeyes.watchface
```

## Aprovação humana pendente
- [ ] Hora pequena, centralizada em arco no topo, acima dos olhos, semelhante ao Aquaticks.
- [ ] Hora correta e formato 12/24h seguindo a configuração do relógio.
- [ ] Pupilas se movem ao inclinar o pulso, sem escaparem do contorno.
- [ ] Toque em cada olho faz somente ele contrair e recuperar em cerca de 1 segundo.
- [ ] Pupila fica recortada durante a contração.
- [ ] Deslizar continua permitindo os gestos normais do Wear OS.
- [ ] No always-on/AOD: hora visível e somente contornos estáticos dos olhos.
- [ ] Acordar a tela restaura olhos e movimento sem travar.
- [ ] Reiniciar preserva seleção do mostrador.
- [ ] Consumo de bateria aceitável ao longo de um dia.

Sem acelerômetro, o XML seleciona posições pseudoaleatórias a cada 2 segundos. O WFF não expõe o temporizador de sensor obsoleto da app e não oferece o mesmo gesto de seguir o dedo arrastado. A app continua disponível para esse gesto. A reação no mostrador é uma contração independente do olho; não há promessa de vibração.

Não fazer merge antes do teste real. As prévias Python verificam composição/layout/recursos, mas não substituem o runtime Wear OS, especialmente para acionamento de TAP na máscara animada.
