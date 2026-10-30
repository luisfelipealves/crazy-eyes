# Crazy Eyes 👀

Dois olhos para brincar no Galaxy Watch: incline o pulso, arraste um dedo ou dê uma cutucada.

## Como funciona

- **Incline o relógio:** as pupilas acompanham suavemente o movimento. O sensor de gravidade é preferido para reduzir tremor; o acelerômetro é a alternativa.
- **Sem sensor ou sem dados por 2 segundos:** os olhos passam a olhar aleatoriamente, com pequenas pausas.
- **Arraste um dedo:** os dois olhos seguem o ponto tocado, inclusive ficando vesgos quando o dedo está entre eles.
- **Toque rápido em um olho:** ele se fecha e se contrai, fica levemente rosado e se recupera em aproximadamente 1 segundo; o outro arregala. O toque usa o feedback tátil do sistema.
- **Toque fora dos olhos:** uma piscada.

A app funciona offline, sem cadastro, anúncios, rastreamento ou permissões de rede/saúde. Ela pausa sensores e animações quando perde foco ou quando a tela apaga. A tela respeita o tempo limite configurado no relógio.

## Instalar e testar

Abra a app **Crazy Eyes** pelo menu do relógio. Requer Wear OS 3 ou superior (API 30+). Desenvolvida para o Galaxy Watch 5 Pro, ainda depende de validação nesse dispositivo.

Com depuração sem fio habilitada e Android platform-tools no computador:

```sh
adb pair IP:PORTA_DE_PAREAMENTO
adb connect IP:PORTA_DE_DEPURACAO
adb install -r crazy-eyes-0.1.0-debug.apk
adb shell am start -n com.luisfelipe.crazyeyes/.MainActivity
```

Veja o [roteiro de teste humano](docs/HUMAN_TESTING.md). Implementação na branch `agent/mvp`; merge após aprovação no relógio.

## Compilar

JDK 17 e Android SDK 36 (build-tools 35.0.0). Configure `ANDROID_HOME` ou `sdk.dir` no seu `local.properties`.

```sh
./gradlew testDebugUnitTest lintDebug assembleDebug
```

O build usa `ci/debug.keystore` quando houver uma chave debug local nesse caminho (senha padrão Android). Essa chave é ignorada pelo Git. Sem ela, usa a assinatura debug padrão do ambiente Android. Para atualizar sem reinstalar, compile com a mesma chave; APKs de ambientes diferentes podem ter certificados diferentes. O CI não recebe a chave local.

APK em `app/build/outputs/apk/debug/app-debug.apk`. O CI também entrega esse APK e os relatórios como artifacts.

## Estrutura

- `EyesEngine.kt`: máquina de estados testável sem Android; inclinação, gestos, piscadas e reação.
- `EyesRenderer.kt`: desenho vetorial usando Canvas.
- `EyesView.kt`: entrada de toque e animação a 30 fps enquanto ativa.
- `MotionInput.kt`: registro e liberação de sensores, filtro e rotação.
- `MainActivity.kt`: tela cheia e controle de ciclo de vida.

As imagens em `app/build/reports/eyes-preview/` são produzidas pelo renderer de produção nos testes Robolectric. A app usa Kotlin e APIs Android, sem frameworks de interface ou bibliotecas de rede.

Versão inicial: **0.1.0**. Não é um mostrador.


## Mostrador Crazy Eyes Face

Além da app, o módulo `watchface` produz um mostrador independente em Watch Face Format 1 (Wear OS4/API33+). A hora fica pequena e curvada no topo, como o `TimeText()` do Aquaticks. Os olhos seguem a inclinação e contraem ao toque. No AOD aparecem a hora e contornos econômicos.

[Instalar e testar o mostrador](docs/WATCHFACE_TESTING.md).

```sh
pip install -r tools/requirements.txt
python -m unittest discover -s tools/tests -v
python -m tools.validate_watchface
./gradlew :watchface:lintDebug :watchface:assembleDebug
python -m tools.validate_watchface --apk watchface/build/outputs/apk/debug/watchface-debug.apk
```

Recursos reproduzíveis: `python tools/watchface_assets.py watchface/src/main/res/drawable-nodpi`.
Prévias de layout: `python -m tools.watchface_preview watchface/src/main/res/raw/watchface.xml preview.png` (`--ambient` para AOD). São prévias Python da definição XML, não screenshots do runtime Wear OS. O schema oficial WFF1 fica em `tools/wff-schema-v1.zip`; ele não é incluído no APK. O teste físico, especialmente toque e persistência após reiniciar, permanece pendente.
