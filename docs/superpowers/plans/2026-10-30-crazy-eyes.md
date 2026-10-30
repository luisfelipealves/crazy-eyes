# Crazy Eyes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Entregar APK Wear OS dos olhos interativos no repositório crazy-eyes.

**Architecture:** Motor Kotlin puro controla estados normalizados e tempo. View Canvas desenha o resultado; Activity e sensor adapter controlam recursos de hardware.

**Tech Stack:** Kotlin 2.2.21, AGP 8.13.2, Gradle 8.13, Android SDK 36, JUnit 4.13.2, Robolectric 4.16.

**Spec:** `docs/superpowers/specs/2026-10-30-crazy-eyes-design.md`

## Global Constraints
- minSdk 30, compile/target 36; Wear OS standalone.
- App offline e sem serviços em segundo plano; main sem implementação até teste humano.
- Sensor obsoleto após 2 segundos; toque até 250 ms; recuperação em 900 ms.

## Review Focus
- Sensor registrado mas sem eventos: olhar aleatório em vez de congelar.
- Arrastar para longe e voltar antes de soltar: não cutucar.
- Pausar durante um toque: limpar gesto e parar recursos.
- Rotação 180°: inclinação deve acompanhar a orientação visual.
- Sem hardware ou registro recusado: toque continua funcionando.

### Task 1: Motor, geometria e testes
**Files:** `app/src/main/java/com/luisfelipe/crazyeyes/EyesEngine.kt`, `app/src/test/java/com/luisfelipe/crazyeyes/EyesEngineTest.kt`, Gradle config.
**Interfaces:** Produz `EyesEngine.frame(nowMs: Long): EyesFrame`, `setTilt(x: Float, y: Float, nowMs: Long)`, `pointerDown/Move/Up`, `cancelTouch`, `resetInput`; geometria em coordenadas 0..1.
- [x] Escrever testes de toque vs arrastar, prioridade do dedo, sensor obsoleto, retorno do sensor, limites e rotação; executá-los e observar falha por motor ausente.
- [x] Implementar motor e executar `./gradlew testDebugUnitTest`; esperar todos os testes verdes.
- [x] Commit do motor e testes.

### Task 2: App Android e renderização
**Files:** `MainActivity.kt`, `EyesView.kt`, `MotionInput.kt`, manifest e recursos; `EyesViewTest.kt`.
**Interfaces:** Consome `EyesFrame`; View recebe eventos Android e converte para coordenadas normalizadas. MotionInput recebe callback `(x: Float, y: Float, timeMs: Long) -> Unit`.
- [x] Escrever testes Robolectric de arrastar/toque/cancelamento e Activity pause/resume; observar falha sem integração.
- [x] Implementar Activity, sensor e desenho; adicionar fallback de registro e rotação.
- [x] Executar `./gradlew testDebugUnitTest lintDebug assembleDebug`; esperar sucesso. Renderizar PNGs em testes para revisão visual.
- [x] Commit da app e testes.

### Task 3: Entrega verificável
**Files:** README, workflow Android e `docs/HUMAN_TESTING.md`.
**Interfaces:** Consome APK e relatórios do Gradle.
- [x] Gerar Gradle wrapper, CI com testes/lint/build e APK como artifact, mantendo material privado de assinatura fora do Git; documentar instalação e cenários de teste no relógio.
- [x] Revisão independente da branch inteira; corrigir problemas importantes com teste de regressão.
- [x] Verificar novamente os comandos, assinatura e manifest do APK; salvar APK e abrir PR em draft sem merge.
