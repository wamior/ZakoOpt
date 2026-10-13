# libs

Положите сюда NeoForge-jar'ы модов, против которых компилируется ZakoOpt (в git они не попадают):

| мод | файл (пример) |
| --- | --- |
| Sodium 0.8.x для 1.21.1 | `sodium-neoforge-0.8.12-beta.1+mc1.21.1.jar` |
| Iris для 1.21.1 | `iris-neoforge-1.8.x+1.21.1.jar` |
| ImmediatelyFast для 1.21.1 | `ImmediatelyFast-NeoForge-1.x+1.21.1.jar` |

Sodium хранит настоящий мод внутри `META-INF/jarjar`; сборка сама распаковывает его в `build/nested-libs`.
