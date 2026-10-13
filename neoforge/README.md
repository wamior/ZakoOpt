# ZakoOpt для NeoForge (форк)

Порт ZakoOpt на NeoForge 1.21.1. Исходники апстрима (`../zakoopt/`) **не меняются** — модуль `1.21.1/`
собирает их «поверх»: берёт слои `common`, `1.21.4`, `sodium-0.8`, применяет regex-замены (`port/rewrite.txt`),
выкидывает несовместимое (`port/exclude.txt`) и подкладывает свои файлы из `1.21.1/src/main/java`
(файл с тем же путём заменяет апстримовский). Из-за этого `git pull upstream main` проходит без конфликтов.

## Сборка
JDK 21, положить jar-ы Sodium/Iris/ImmediatelyFast в `1.21.1/libs/` (см. `libs/README.md`), затем:

    cd neoforge && ./gradlew :1.21.1:build

## Получение изменений апстрима

    git remote add upstream https://github.com/3ako/ZakoOpt   # один раз
    git pull upstream main
    neoforge/tools/sync-status.sh                              # что изменилось и что требует адаптации

Затем попросите Claude адаптировать: новые миксины либо подхватятся автоматически, либо их нужно
добавить в `exclude.txt` / написать версию под 1.21.1 в `1.21.1/src/main/java`. После адаптации обновить
`neoforge/UPSTREAM_BASE` (скрипт напомнит).

## Не поддерживается на 1.21.1 (скрыто в настройках)
Фичи, завязанные на EntityRenderState/FrameGraph/Tracy (LOD сущностей по состоянию, ring buffer, frame fence,
кэш спавнеров, LOD предметов, пропуск outline, часть частиц/шрифта). Список — `1.21.1/port/exclude.txt`.

## Проверка без игры
`tools/check_mixins.py` + `tools/classindex.py` статически проверяют цели миксинов по jar-ам Minecraft/Sodium.
Сборка через Gradle и запуск в игре в облаке не проверялись.
