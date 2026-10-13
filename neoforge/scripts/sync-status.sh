#!/bin/bash
# Показывает, что изменилось в апстриме (zakoopt/) с момента последней адаптации под NeoForge.
# usage: neoforge/scripts/sync-status.sh [version-module, default 1.21.1]
set -e
cd "$(dirname "$0")/../.."
V=${1:-1.21.1}
BASE=$(cat neoforge/UPSTREAM_BASE)
P=neoforge/$V/port
echo "== изменения zakoopt/ с $BASE =="
git diff --name-status "$BASE" HEAD -- zakoopt | grep -E '/src/main/(java|resources)/' || { echo "нет изменений"; exit 0; }
echo
echo "== затронуты файлы, которые мы переопределили или исключили (нужна ручная адаптация) =="
git diff --name-only "$BASE" HEAD -- zakoopt | sed -E 's#^zakoopt/[^/]+/src/main/java/##' | sort -u | while read f; do
  [ -f "neoforge/$V/src/main/java/$f" ] && echo "OVERRIDE  $f"
  grep -qxF "$f" "$P/exclude.txt" 2>/dev/null && echo "EXCLUDED  $f"
done
echo
echo "После адаптации: echo \$(git rev-parse HEAD) > neoforge/UPSTREAM_BASE"
