# Crazy Eyes Watch Face Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** APK WFF com olhos e hora em arco no topo, como Aquaticks.
**Architecture:** Módulo Android resource-only; pupilas Gyro, máscara WebP por toque e contornos AOD. Ferramentas Python geram recursos e verificam schema e imagens.
**Tech Stack:** WFF1, AGP8.13.2, SDK36/min33; Pillow, xmlschema (XSD1.1).
**Spec:** `docs/superpowers/specs/2026-10-30-crazy-eyes-watchface-design.md`

## Global Constraints
- APK separado sem código, minSdk33, WFF1; app existente continua disponível.
- Hora pequena em arco no topo, 12/24h do dispositivo. AOD <15% de pixels acesos.
- Sem material privado de assinatura no Git e sem merge automático.

## Review Focus
- Pupila não pode ficar fora do olho quando a máscara contrai.
- Hora precisa estar dentro da tela circular e acima dos olhos.
- Ausência de acelerômetro deve continuar com animação suave.
- Recursos interativos precisam desaparecer completamente no AOD.
- APK precisa ser reconhecido como WFF e não conter DEX.

### Task 1: Recursos e definição WFF
**Files:** `tools/watchface_assets.py`, `tools/tests/test_watchface_assets.py`, `watchface/src/main/res/`, `tools/validate_watchface.py`, schema oficial em `tools/wff-schema-v1.zip`.
**Interfaces:** `generate(output: Path)` cria PNG/WebP e `render_preview(xml_path: Path, ambient: bool)` desenha uma prévia a partir da definição para QA; `validate(root: Path)` verifica schema/recursos/limites.
- [ ] Escrever teste de recuperação e confinamento da máscara animada; observar falha sem gerador.
- [ ] Implementar gerador e XML WFF; validar schema oficial e recursos.
- [ ] Testar orçamento AOD, recuperação da máscara, hora e confinamento geométrico; inspecionar prévias.

### Task 2: APK, CI e entrega
**Files:** `watchface/build.gradle.kts`, manifest, settings, workflow, `docs/WATCHFACE_TESTING.md`, README.
**Interfaces:** Gradle `:watchface:lintDebug :watchface:assembleDebug`, Python validator; APK e artifacts separados.
- [ ] Configurar módulo resource-only e CI; compilar app + mostrador e executar testes existentes.
- [ ] Inspecionar APK/manifest e renderizações; revisão independente sem alterar árvore.
- [ ] Corrigir problemas importantes, salvar APK, abrir PR draft e documentar teste real pendente.
