# Crazy Eyes Face — teste no relógio

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
