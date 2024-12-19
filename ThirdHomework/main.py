import os
from typing import Any
import yaml
import operator
import re

# static
class Loader:
    def __init__(self):
        raise Exception(f"Class {Loader.__name__} is a static class and cannot be instantiated")

    @staticmethod
    def load_trainee(trainee_text: str) -> Any:
        """
        Translates text in the trn (trainee) language into a structure.
        :param trainee_text: Text in trn (trainee).
        :return: Structure filled with data from the read text.
        """
        # Remove multi-line comments
        def remove_multiline_comments(text):
            pattern = r'\(\*.*?\*\)'
            cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
            return cleaned_text

        cleaned_text = remove_multiline_comments(trainee_text)

        # Initialize a dictionary to hold variables
        variables = {}

        # Process each line
        lines = cleaned_text.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue  # Skip empty lines

            # Match variable assignment
            match = re.match(r'^(set)\s*([_a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(.*);$', line)
            if match:
                var_name = match.group(2).strip()
                value_str = match.group(3).strip()

                # Check if it's a table
                if value_str.startswith('['):
                    # Start of a table block
                    table_lines = []
                    # Remove 'table([' from the line
                    remainder = value_str[len('['):].strip()
                    if remainder.endswith(']'):
                        # Single-line table
                        table_content = remainder[:-1].strip()
                        table_lines = [table_content]
                        i += 1
                    else:
                        # Multi-line table
                        # Add the remainder of the current line if any
                        if remainder:
                            table_lines.append(remainder)
                        i += 1
                        while i < len(lines):
                            table_line = lines[i].strip()
                            if table_line.endswith(']'):
                                # End of table block
                                # Remove '])' from the line
                                table_line = table_line[:-1].strip()
                                if table_line:
                                    table_lines.append(table_line)
                                break
                            else:
                                table_lines.append(table_line)
                            i += 1
                        else:
                            raise ValueError("Table definition not closed with ']'")

                    # Combine table lines into a single string and split by commas
                    table_content = ' '.join(table_lines)
                    # Split the content by commas, accounting for possible commas within braces or parentheses
                    items = Loader.split_table_items(table_content)

                    # Parse the table
                    table = {}
                    for item in items:
                        table_line = item.strip()
                        if not table_line:
                            continue  # Skip empty items
                        # Match key-value pairs inside the table
                        kv_match = re.match(r'^([_a-zA-Z][_a-zA-Z0-9]*)\s*=>\s*(.*)$', table_line)
                        if kv_match:
                            key = kv_match.group(1)
                            value_str = kv_match.group(2).strip()

                            # Parse the value
                            value = Loader.parse_value(value_str, variables)
                            table[key] = value
                        else:
                            raise ValueError(f"Invalid syntax in table: {table_line}")

                    # Assign the table to the variable
                    variables[var_name] = table
                else:
                    # Parse the value
                    value = Loader.parse_value(value_str, variables)
                    # Assign the variable
                    variables[var_name] = value
                    i += 1
            else:
                raise ValueError(f"Invalid syntax: {line}")
        return variables

    @staticmethod
    def split_table_items(table_content):
        """
        Split table content into key-value pairs, handling nested structures.
        """
        items = []
        current_item = ''
        brace_count = 0
        for char in table_content:
            if char == '{' or char == '(' or char == '[':
                brace_count += 1
            elif char == '}' or char == ')' or char == ']':
                brace_count -= 1
            if char == ',' and brace_count == 0:
                items.append(current_item)
                current_item = ''
            else:
                current_item += char
        if current_item:
            items.append(current_item.strip())
        return items

    @staticmethod
    def parse_value(value_str, variables):
        """
        Parse a value string and return the corresponding Python value.
        """
        value_str = value_str.strip()
        if value_str.lstrip("-").isdigit():
            # Integer value
            return int(value_str)
        elif value_str.startswith('\"') and value_str.endswith('\"'):
            # String value
            return value_str[1:-1]  # Remove " and ending "
        elif value_str.startswith('@(') and value_str.endswith(')'):
            # Expression
            expr = value_str[2:-1]  # Remove @ and surrounding parentheses
            tokens = expr.strip().split()
            return Loader.evaluate_expression(tokens, variables)
        elif value_str.startswith('{') and value_str.endswith('}'):
            # Array
            array_content = value_str[1:-1].strip()  # Remove { and }
            items = Loader.split_array_items(array_content)
            value = []
            for item_str in items:
                item_value = Loader.parse_value(item_str, variables)
                value.append(item_value)
            return value
        elif value_str in variables:
            # Variable assignment from another variable
            return variables[value_str]
        else:
            raise ValueError(f"Invalid value: {value_str}")

    @staticmethod
    def split_array_items(array_content):
        """
        Split array content into items, handling nested structures.
        """
        items = []
        current_item = ''
        brace_count = 0
        for char in array_content:
            if char == '{' or char == '(' or char == '[':
                brace_count += 1
            elif char == '}' or char == ')' or char == ']':
                brace_count -= 1
            if char == '.' and brace_count == 0:
                items.append(current_item.strip())
                current_item = ''
            else:
                current_item += char
        if current_item:
            items.append(current_item.strip())
        return items

    @staticmethod
    def evaluate_expression(tokens, constants):
        """
        Evaluate constant expression in postfix notation.
        Supports addition and ord() function.
        """
        stack = []
        first_token = tokens[0]
        tokens = tokens[1:]

        # Operators and functions
        operators = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
        }

        functions = {
            'ord': lambda x: ord(x) if isinstance(x, str) and len(x) == 1 else ValueError("ord() expects a single character"),
            'abs': lambda x: abs(x) if isinstance(x, int) else ValueError("abs() expects a number"),
        }
        for token in tokens:
            if token.lstrip('-').isdigit():
                stack.append(int(token))
            elif token.startswith('\"') and token.endswith('\"'):
                stack.append(token[1:-1])  # Remove " and "
            elif token in constants:
                stack.append(constants[token])
            else:
                raise ValueError(f"Unknown token '{token}' in expression")
        
        if first_token in operators:
            if len(stack) < 2:
                raise ValueError("Insufficient operands for operator")
            b = stack.pop()
            a = stack.pop()
            result = operators[first_token](a, b)
            stack.append(result)
        elif first_token in functions:
            if not stack:
                raise ValueError("Insufficient operands for function")
            a = stack.pop()
            result = functions[first_token](a)
            if isinstance(result, Exception):
                raise result
            stack.append(result)
        
        if len(stack) != 1:
            raise ValueError("Invalid expression")
        return stack[0]

    @staticmethod
    def get_yaml(struct: Any) -> str:
        """
        Translates any type of object with any fields to YAML.
        :param struct: Object to save.
        :return: Configuration in YAML.
        """
        return yaml.dump(struct, allow_unicode=True)

if __name__ == "__main__":
    test_file_path = "input.txt"

    try:
        with open(test_file_path, 'r', encoding='utf-8') as file:
            trainee_text = file.read()

        struct = Loader.load_trainee(trainee_text)

        if struct is not None:
            yaml_output = Loader.get_yaml(struct)
            print(yaml_output)
            with open("output.yaml", 'w', encoding='utf-8') as file:
                file.write(yaml_output)
        else:
            print("Failed to parse the configuration.")

    except FileNotFoundError:
        print(f"File '{test_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")