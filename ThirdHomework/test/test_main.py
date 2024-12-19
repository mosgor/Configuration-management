import unittest
from main import Loader

class TestLoader(unittest.TestCase):
    def test_load_trainee(self):
        trainee_text = """
        (*
            This is a comment
        *)
        set num = 42;
        set str = "Hello";
        set arr = { 1. 2. 3. };
        set table = [key1 => 10, key2 => "value"];
        set expr = @(+ num 1);
        """

        expected_output = {
            'num': 42,
            'str': "Hello",
            'arr': [1, 2, 3],
            'table': {'key1': 10, 'key2': "value"},
            'expr': 43
        }

        result = Loader.load_trainee(trainee_text)
        self.assertEqual(result, expected_output)

    def test_split_table_items(self):
        table_content = "key1 => 10, key2 => \"value\""
        expected_items = ["key1 => 10", "key2 => \"value\""]

        result = Loader.split_table_items(table_content)
        self.assertEqual(result, expected_items)

    def test_split_array_items(self):
        array_content = "1. 2. { 3. 4. }"
        expected_items = ["1", "2", "{ 3. 4. }"]

        result = Loader.split_array_items(array_content)
        self.assertEqual(result, expected_items)

    def test_parse_value(self):
        variables = {'var': 10}

        # Integer
        self.assertEqual(Loader.parse_value("42", variables), 42)

        # String
        self.assertEqual(Loader.parse_value("\"Hello\"", variables), "Hello")

        # Array
        self.assertEqual(Loader.parse_value("{ 1. 2. 3. }", variables), [1, 2, 3])

        # Variable reference
        self.assertEqual(Loader.parse_value("var", variables), 10)

        # Expression
        self.assertEqual(Loader.parse_value("@(+ var 2)", variables), 12)

    def test_evaluate_expression(self):
        constants = {'num': 5}

        # Simple addition
        self.assertEqual(Loader.evaluate_expression(["+", "2", "3"], constants), 5)

        # Variable usage
        self.assertEqual(Loader.evaluate_expression(["+", "num", "2"], constants), 7)

        # Function usage (ord)
        self.assertEqual(Loader.evaluate_expression(["ord", "\"A\""], constants), 65)

if __name__ == "__main__":
    unittest.main()
