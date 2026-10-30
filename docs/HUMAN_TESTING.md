# Teste no Galaxy Watch 5 Pro — 0.1.0

Estado: **HUMAN_TESTING pendente**. Não fazer merge até aprovação no dispositivo.

## Instalar
No relógio, ative Opções do desenvolvedor > Depuração ADB / Depuração sem fio. No computador com Android platform-tools:

```sh
adb pair IP_DO_RELOGIO:PORTA_DE_PAREAMENTO
adb connect IP_DO_RELOGIO:PORTA_DE_DEPURACAO
adb install -r crazy-eyes-0.1.0-debug.apk
adb shell am start -n com.luisfelipe.crazyeyes/.MainActivity
```
As portas de pareamento e depuração são diferentes e podem mudar. Algumas versões do Wear OS usam somente `adb connect`. A app aparece no menu como **Crazy Eyes**.

## Roteiro
- [ ] Os dois olhos cabem na tela redonda e aparecem em fundo preto, sem barras nem texto.
- [ ] Inclinar o pulso para os quatro lados move as pupilas suavemente; verificar também com orientação invertida do relógio.
- [ ] Arrastar um dedo pelos olhos e entre eles: ambos seguem o dedo, convergindo quando necessário.
- [ ] Arrastar para longe e voltar antes de soltar não produz cutucada.
- [ ] Toque curto em cada olho: olho fecha/contrai, fica levemente rosado, outro arregala; recuperação em aproximadamente 1 segundo. Feedback tátil respeita configuração do relógio.
- [ ] Manter o dedo parado por mais de 250 ms e soltar: não cutuca.
- [ ] Tocar com dois dedos ou receber interrupção durante gesto: não ficar preso no toque.
- [ ] Soltar após arrastar: movimento do pulso volta suavemente.
- [ ] Usar app, apagar tela, reativar, sair e voltar: sem travar nem manter a tela ligada à força.
- [ ] Observar piscadas ocasionais e contorno das pupilas nas bordas dos olhos.

Fallback sem sensores é coberto nos testes automatizados. Para validar visualmente, use emulador sem sensores disponíveis ou interrompa a entrega de eventos por pelo menos 2 segundos: os olhos devem olhar aleatoriamente. Retomada dos eventos deve devolver o controle ao pulso.

A instalação usa assinatura de desenvolvimento. Guarde o mesmo keystore para atualizar versões sem reinstalar. A app não armazena dados do usuário.
