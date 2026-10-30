# Crazy Eyes Face — teste no relógio

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
