Задание №3 - 11 ВАРИАНТ

Разработан инструмент командной строки для учебного конфигурационного
языка, синтаксис которого приведен далее. Этот инструмент преобразует текст из
входного формата в выходной. Синтаксические ошибки выявляются с выдачей
сообщений.  
Входной текст на учебном конфигурационном языке принимается из
стандартного ввода. Выходной текст на языке yaml попадает в файл, путь к
которому задан ключом командной строки.

Многострочные комментарии:
```
(*
    This is a comment
*)
```

Массивы:
```
{ значение. значение. значение. ... }
```

Имена:
```
[_a-zA-Z][_a-zA-Z0-9]
```

Значения:
- Числа.
- Строки.
- Массивы.
- Словари.

Строки:
```
"Это строка"
```

Объявление константы на этапе трансляции:
```
set имя = значение;
```
Вычисление константного выражения на этапе трансляции (префиксная
форма), пример:
```
@(+ имя 1)
```
Результатом вычисления константного выражения является значение.  

Для константных вычислений определены операции и функции:
1. Сложение.
2. Вычитание.
3. Умножение.
4. Деление
5. abs().
6. ord().

Все конструкции учебного конфигурационного языка (с учетом их
возможной вложенности) покрыты тестами.