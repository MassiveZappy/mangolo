#!/usr/bin/env python3
"""
Mangolo Language - Fixed Parser
"""
import argparse
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

class ParseError(Exception):
    """Base exception for parsing errors with line and column information."""
    def __init__(self, message: str, line: int, column: int, file_path: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.file_path = file_path
        file_info = f" in {file_path}" if file_path else ""
        super().__init__(f"{message} at line {line}, column {column}{file_info}")

def identifyDataType(value):
    """Identify and convert string data to appropriate Python types."""
    if value is None or value == "":
        return None

    # String types
    if isinstance(value, str):
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]  # Return the string without quotes
        elif value.startswith("'") and value.endswith("'"):
            return value[1:-1]  # Return the string without quotes
        elif value.isdigit():
            return int(value)  # Convert to integer
        elif '.' in value and value.replace('.', '', 1).isdigit():
            return float(value)  # Convert to float
        elif value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.lower() == 'null':
            return None

    return value

class MangoloTreeFileReader:
    """Reader for mangolo.tree files."""

    @staticmethod
    def loads(data):
        """Parse tree file content into structured data."""
        output = []
        line_number = 0

        for line in data.splitlines():
            line_number += 1
            # Remove comments
            line = line.split('#', 1)[0].strip()

            if not line:  # Skip empty lines
                continue

            parts = line.split(None, 1)
            if len(parts) < 2:
                print(f"Warning: Invalid tree entry on line {line_number}: '{line}'")
                continue

            mango_location, mango_type = parts

            output.append({
                'priority': len(output) + 1,
                'mango_location': mango_location,
                'mango_type': mango_type
            })

        return output

    @staticmethod
    def load(path):
        """Read and parse a tree file from path."""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = file.read()
            return MangoloTreeFileReader.loads(data)
        except Exception as e:
            print(f"Error reading tree file: {e}")
            raise

class MangoloMangoFileReader:
    """Reader for .mango configuration files."""

    @staticmethod
    def loads(data, file_path=None):
        """Parse TOML-like mango file content."""
        output = {}
        line_number = 0

        # Split into clean lines (removing comments)
        clean_lines = []
        for line in data.splitlines():
            line_number += 1
            # Remove comments but keep the line for error reporting
            clean_line = line.split('#', 1)[0].strip()
            if clean_line:
                clean_lines.append((clean_line, line_number))

        # Process lines
        keychain = "global"  # Default section
        output[keychain] = {}

        i = 0
        while i < len(clean_lines):
            line, line_num = clean_lines[i]

            # Handle section headers [section]
            if line.startswith('[') and line.endswith(']'):
                keychain = line[1:-1].strip()
                if keychain not in output:
                    output[keychain] = {}
                i += 1
                continue

            # Handle key-value pairs
            if '=' in line:
                key, value_part = line.split('=', 1)
                key = key.strip()
                value_part = value_part.strip()

                # Handle different value types
                if value_part == "":
                    # Empty value
                    output[keychain][key] = ""
                    i += 1
                elif value_part.startswith('"') and value_part.endswith('"') and '"' not in value_part[1:-1].replace('\\"', ''):
                    # Simple quoted string
                    output[keychain][key] = value_part[1:-1].replace('\\"', '"')
                    i += 1
                elif value_part.startswith("'") and value_part.endswith("'") and "'" not in value_part[1:-1].replace("\\'", "'"):
                    # Simple quoted string with single quotes
                    output[keychain][key] = value_part[1:-1].replace("\\'", "'")
                    i += 1
                elif value_part.startswith('"""'):
                    # Multi-line string with triple double quotes
                    if value_part.endswith('"""') and len(value_part) > 6:
                        # Triple quoted string on a single line
                        output[keychain][key] = value_part[3:-3]
                        i += 1
                    else:
                        # Start of a multi-line string
                        string_value = value_part[3:]
                        i += 1
                        while i < len(clean_lines):
                            next_line, next_line_num = clean_lines[i]
                            if '"""' in next_line:
                                end_idx = next_line.find('"""')
                                string_value += '\n' + next_line[:end_idx]
                                break
                            string_value += '\n' + next_line
                            i += 1
                        if i >= len(clean_lines):
                            raise ParseError("Unterminated multi-line string", line_num, len(line), file_path)
                        output[keychain][key] = string_value
                        i += 1
                elif value_part.startswith("'''"):
                    # Multi-line string with triple single quotes
                    if value_part.endswith("'''") and len(value_part) > 6:
                        # Triple quoted string on a single line
                        output[keychain][key] = value_part[3:-3]
                        i += 1
                    else:
                        # Start of a multi-line string
                        string_value = value_part[3:]
                        i += 1
                        while i < len(clean_lines):
                            next_line, next_line_num = clean_lines[i]
                            if "'''" in next_line:
                                end_idx = next_line.find("'''")
                                string_value += '\n' + next_line[:end_idx]
                                break
                            string_value += '\n' + next_line
                            i += 1
                        if i >= len(clean_lines):
                            raise ParseError("Unterminated multi-line string", line_num, len(line), file_path)
                        output[keychain][key] = string_value
                        i += 1
                elif value_part.startswith('['):
                    # Array/list
                    if value_part.endswith(']') and self._is_balanced_array(value_part):
                        # Simple array on a single line
                        try:
                            array_value = MangoloMangoFileReader._parse_array(value_part)
                            output[keychain][key] = array_value
                        except Exception as e:
                            raise ParseError(f"Invalid array syntax: {e}", line_num, line.find(value_part) + 1, file_path)
                        i += 1
                    else:
                        # Start of a multi-line array
                        array_text = value_part
                        i += 1
                        while i < len(clean_lines):
                            next_line, next_line_num = clean_lines[i]
                            array_text += next_line
                            if ']' in next_line and MangoloMangoFileReader._is_balanced_array(array_text):
                                break
                            i += 1
                        if i >= len(clean_lines) or not MangoloMangoFileReader._is_balanced_array(array_text):
                            raise ParseError("Unterminated array", line_num, len(line), file_path)
                        try:
                            array_value = MangoloMangoFileReader._parse_array(array_text)
                            output[keychain][key] = array_value
                        except Exception as e:
                            raise ParseError(f"Invalid array syntax: {e}", line_num, line.find(value_part) + 1, file_path)
                        i += 1
                else:
                    # Simple scalar value (number, boolean, etc.)
                    value = identifyDataType(value_part)
                    output[keychain][key] = value
                    i += 1
            else:
                # Invalid line (not a section or key-value)
                raise ParseError(f"Invalid line format", line_num, 1, file_path)

        return output

    @staticmethod
    def _parse_array(array_text):
        """Parse array text into a Python list, handling nested arrays and quoted strings."""
        # Basic validation
        array_text = array_text.strip()
        if not (array_text.startswith('[') and array_text.endswith(']')):
            raise ValueError("Not a valid array format")

        if array_text == '[]':
            return []

        # Remove outer brackets
        content = array_text[1:-1].strip()

        # Split by commas, respecting quotes and nested structures
        items = []
        current_item = ''
        in_quotes = False
        quote_char = None
        bracket_depth = 0
        brace_depth = 0

        for char in content:
            # Handle quotes
            if char in ('"', "'") and (not in_quotes or quote_char == char):
                if in_quotes and quote_char == char and current_item and current_item[-1] != '\\':
                    in_quotes = False
                    quote_char = None
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
                current_item += char
            # Handle brackets (for nested arrays)
            elif char == '[' and not in_quotes:
                bracket_depth += 1
                current_item += char
            elif char == ']' and not in_quotes:
                bracket_depth -= 1
                current_item += char
            # Handle braces (for objects)
            elif char == '{' and not in_quotes:
                brace_depth += 1
                current_item += char
            elif char == '}' and not in_quotes:
                brace_depth -= 1
                current_item += char
            # Handle commas
            elif char == ',' and not in_quotes and bracket_depth == 0 and brace_depth == 0:
                items.append(current_item.strip())
                current_item = ''
            else:
                current_item += char

        # Add the last item if needed
        if current_item.strip():
            items.append(current_item.strip())

        # Convert each item to its appropriate type
        result = []
        for item in items:
            if not item:  # Skip empty items
                continue
            result.append(identifyDataType(item))

        return result

    @staticmethod
    def _is_balanced_array(text):
        """Check if brackets are balanced in array text, ignoring quoted content."""
        stack = []
        in_quotes = False
        quote_char = None
        escaped = False

        for char in text:
            if escaped:
                escaped = False
                continue

            if char == '\\':
                escaped = True
                continue

            if char in ('"', "'") and (not in_quotes or quote_char == char):
                if in_quotes and quote_char == char:
                    in_quotes = False
                    quote_char = None
                else:
                    in_quotes = True
                    quote_char = char
                continue

            if in_quotes:
                continue

            if char == '[':
                stack.append('[')
            elif char == ']':
                if not stack or stack[-1] != '[':
                    return False
                stack.pop()

        return len(stack) == 0

    @staticmethod
    def load(path):
        """Read and parse a .mango file from path."""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = file.read()
            return MangoloMangoFileReader.loads(data, path)
        except Exception as e:
            print(f"Error parsing mango file: {e}")
            raise

class MangoloSliceFileReader:
    """Reader for .slice schema files."""

    @staticmethod
    def loads(data, file_path=None):
        """Parse .slice schema file content."""
        output = {}
        current_section = None
        section_content = []
        line_number = 0

        # Process lines
        for line in data.splitlines():
            line_number += 1
            # Remove comments
            line = line.split('#', 1)[0].strip()

            if not line:  # Skip empty lines
                continue

            # Check for section headers
            if line.startswith('[') and line.endswith(']'):
                # Save previous section if any
                if current_section:
                    output[current_section] = MangoloSliceFileReader._parse_section_content(
                        current_section, section_content, file_path
                    )

                # Start new section
                current_section = line[1:-1].strip()
                section_content = []
            else:
                if current_section is None:
                    raise ParseError("Content outside of section", line_number, 1, file_path)
                section_content.append((line, line_number))

        # Handle the last section
        if current_section:
            output[current_section] = MangoloSliceFileReader._parse_section_content(
                current_section, section_content, file_path
            )

        return output

    @staticmethod
    def _parse_section_content(section_name, content, file_path):
        """Parse the content of a section based on its type."""
        if section_name == "object":
            return MangoloSliceFileReader._parse_object_section(content, file_path)
        elif section_name == "indexes":
            return MangoloSliceFileReader._parse_indexes_section(content, file_path)
        elif section_name == "permissions":
            return MangoloSliceFileReader._parse_permissions_section(content, file_path)
        elif section_name == "validations":
            return MangoloSliceFileReader._parse_validations_section(content, file_path)
        else:
            return MangoloSliceFileReader._parse_generic_section(content, file_path)

    @staticmethod
    def _parse_object_section(content, file_path):
        """Parse object section with field definitions."""
        fields = []

        for line, line_num in content:
            # Split field name and type definition
            if ":" not in line:
                raise ParseError("Invalid field definition, missing colon", line_num, 1, file_path)

            name, type_def = line.split(":", 1)
            name = name.strip()
            type_def = type_def.strip()

            # Split type and modifiers
            parts = type_def.split()
            if not parts:
                raise ParseError(f"Missing type for field '{name}'", line_num, line.find(":") + 1, file_path)

            field_type = parts[0]
            modifiers = parts[1:] if len(parts) > 1 else []

            # Parse any structured modifiers
            parsed_modifiers = []
            for mod in modifiers:
                if "(" in mod and mod.endswith(")"):
                    mod_name, mod_params = mod.split("(", 1)
                    mod_params = mod_params[:-1]  # Remove closing parenthesis
                    parsed_modifiers.append({
                        "name": mod_name,
                        "params": mod_params
                    })
                else:
                    parsed_modifiers.append(mod)

            fields.append({
                "name": name,
                "type": field_type,
                "modifiers": parsed_modifiers
            })

        return fields

    @staticmethod
    def _parse_indexes_section(content, file_path):
        """Parse indexes section."""
        indexes = {}

        for line, line_num in content:
            if ":" not in line:
                raise ParseError("Invalid index definition, missing colon", line_num, 1, file_path)

            name, definition = line.split(":", 1)
            name = name.strip()

            # Parse the index definition (expected to be JSON-like)
            try:
                # Simple parsing for demonstration - in real code, use a proper parser
                definition = definition.strip()
                if definition.startswith("{") and definition.endswith("}"):
                    # Very basic parsing - in real code use a proper JSON parser
                    definition = definition[1:-1].strip()
                    parts = definition.split(",")
                    index_def = {}

                    for part in parts:
                        part = part.strip()
                        if ":" in part:
                            key, value = part.split(":", 1)
                            key = key.strip().strip('"\'')
                            value = value.strip()

                            # Handle array notation
                            if value.startswith("[") and value.endswith("]"):
                                value = [v.strip().strip('"\'') for v in value[1:-1].split(",")]
                            else:
                                value = value.strip('"\'')

                            index_def[key] = value

                    indexes[name] = index_def
                else:
                    raise ValueError("Expected object definition")
            except Exception as e:
                raise ParseError(f"Invalid index definition: {e}", line_num, line.find(definition), file_path)

        return indexes

    @staticmethod
    def _parse_permissions_section(content, file_path):
        """Parse permissions section."""
        permissions = {}

        for line, line_num in content:
            if ":" not in line:
                raise ParseError("Invalid permission definition, missing colon", line_num, 1, file_path)

            operation, roles = line.split(":", 1)
            operation = operation.strip()

            # Parse roles (expected to be array or object)
            try:
                roles = roles.strip()

                if roles.startswith("[") and roles.endswith("]"):
                    # Array of roles
                    roles_list = []
                    roles_content = roles[1:-1].strip()

                    if roles_content:
                        for role in roles_content.split(","):
                            role = role.strip().strip('"\'')
                            roles_list.append(role)

                    permissions[operation] = roles_list
                elif roles.startswith("{") and roles.endswith("}"):
                    # Object with conditional permissions
                    permissions[operation] = roles  # Simplified - would need proper parsing
                else:
                    raise ValueError("Expected array or object for roles")
            except Exception as e:
                raise ParseError(f"Invalid permission definition: {e}", line_num, line.find(roles), file_path)

        return permissions

    @staticmethod
    def _parse_validations_section(content, file_path):
        """Parse validations section with rule blocks."""
        validations = []

        i = 0
        while i < len(content):
            line, line_num = content[i]

            # Find rule definitions
            if line.startswith("rule "):
                rule_name = line[5:].split("{")[0].strip()

                # Collect all lines for this rule
                rule_lines = []
                brace_depth = 0

                # Check if rule begins on this line
                if "{" in line:
                    brace_depth += line.count("{") - line.count("}")
                    rule_lines.append(line)

                # Continue adding lines until closing brace
                i += 1
                while i < len(content) and brace_depth > 0:
                    next_line, next_line_num = content[i]
                    rule_lines.append(next_line)
                    brace_depth += next_line.count("{") - next_line.count("}")
                    i += 1

                # Parse rule content
                rule_content = " ".join(rule_lines)

                try:
                    # Extract validate and message parts
                    validate_match = rule_content.find("validate:")
                    message_match = rule_content.find("message:")
                    condition_match = rule_content.find("condition:")

                    rule = {"name": rule_name}

                    if condition_match >= 0:
                        condition_end = message_match if message_match >= 0 else validate_match
                        if condition_end >= 0:
                            condition = rule_content[condition_match + 10:condition_end].strip()
                            condition = condition.rstrip(",").strip()
                            rule["condition"] = condition

                    if validate_match >= 0:
                        validate_end = message_match if message_match >= 0 else rule_content.find("}", validate_match)
                        if validate_end >= 0:
                            validate = rule_content[validate_match + 9:validate_end].strip()
                            validate = validate.rstrip(",").strip()
                            rule["validate"] = validate

                    if message_match >= 0:
                        message_end = rule_content.find("}", message_match)
                        if message_end >= 0:
                            message = rule_content[message_match + 8:message_end].strip()
                            message = message.strip('"\'')
                            rule["message"] = message

                    validations.append(rule)
                except Exception as e:
                    raise ParseError(f"Invalid validation rule: {e}", line_num, 1, file_path)
            else:
                i += 1

        return validations

    @staticmethod
    def _parse_generic_section(content, file_path):
        """Parse a generic section as key-value pairs."""
        result = {}

        for line, line_num in content:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Try to convert value to appropriate type
                result[key] = identifyDataType(value)
            else:
                # Just store the line as a string
                result[f"line_{line_num}"] = line

        return result

    @staticmethod
    def load(path):
        """Read and parse a .slice file from path."""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = file.read()
            return MangoloSliceFileReader.loads(data, path)
        except Exception as e:
            print(f"Error parsing slice file: {e}")
            raise

def load_project(path):
    """Load a Mangolo project from the specified path."""
    # Verify the project directory exists
    if not os.path.isdir(path):
        print(f"Error: Project directory '{path}' does not exist.")
        return None

    # Check for mangolo.tree file
    tree_file_path = os.path.join(path, 'mangolo.tree')
    if not os.path.isfile(tree_file_path):
        print(f"Error: mangolo.tree file not found in project directory.")
        return None

    project_data = {
        'tree': None,
        'components': {}
    }

    try:
        # Load the tree file
        print(f"Reading project structure from {tree_file_path}...")
        project_data['tree'] = MangoloTreeFileReader.load(tree_file_path)

        # Process each entry in the tree
        for entry in project_data['tree']:
            mango_location = entry['mango_location']
            mango_type = entry['mango_type']

            # Construct full path
            file_path = os.path.join(path, mango_location)

            print(f"Processing {mango_type}: {mango_location}")

            # Load based on file type
            if mango_location.endswith('.mango'):
                project_data['components'][mango_location] = {
                    'type': mango_type,
                    'data': MangoloMangoFileReader.load(file_path)
                }
            elif mango_location.endswith('.slice'):
                project_data['components'][mango_location] = {
                    'type': mango_type,
                    'data': MangoloSliceFileReader.load(file_path)
                }
            else:
                print(f"Warning: Unsupported file type for {mango_location}")

        return project_data

    except Exception as e:
        print(f"Error loading project: {e}")
        return None

def main():
    """Main entry point for the Mangolo interpreter."""
    # Verify Python version
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 10):
        print("Mangolo requires Python 3.10 or higher.")
        exit(1)

    print("-" * 50)
    print("Mangolo Language")
    print("A programming language designed for creating frontend libraries")
    print("that interact with backend database management systems.")
    print("-" * 50)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Mangolo Language Interpreter')
    parser.add_argument('--project', '-p', default=os.getcwd(),
                        help='Project directory (defaults to current directory)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    args = parser.parse_args()

    # Load and process project
    project_data = load_project(args.project)

    if project_data:
        if args.verbose:
            import json
            print("\nProject Data:")
            print(json.dumps(project_data, indent=2, default=str))

        print("\nProject loaded successfully!")
    else:
        print("\nFailed to load project.")
        exit(1)

if __name__ == "__main__":
    main()
