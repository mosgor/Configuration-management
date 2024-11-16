# Практическая работа №2

**Цель работы:** составить программу - визуализатор зависимостей ***пакета Python***.  
Для графического представления используется ***mermaid***.

Практическая работа содержит следующие функции:
- `parse_xml_config` - разбирает конфигурационный xml и сохраняет настройки из него.
- `get_dependencies` - обращается к pip и получает зависимости запрошенного пакета.
- `build_dependency_graph` - форматирует зависимости в формат `A --> B`.
- `generate_mermaid_script` - форматирует список зависимостей в формат mermaid скрипта.
- `save_mermaid_script` - сохраняет mermaid срипт в отдельный файл.
- `visualize_graph` - передаёт скрипт в утилиту mermaid-cli и визуализирует скрипт.

*Все* функции покрыты тестами.

**Вывод:** в результатах выполненной работы была написана программа визуализирующая зависимости пакетов Python.  
Все функции покрыты тестами.