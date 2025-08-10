"""
Mangolo Language
"""
import argparse
import os
import mongoloErrors
import mongoloFileReaders
import knive

def identifyDataType(value):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]  # Return the string without quotes
    elif value.startswith("'") and value.endswith("'"):
        return value[1:-1]  # Return the string without quotes
    elif value.isdigit():
        return int(value)  # Convert to integer
    elif '.' in value and value.replace('.', '', 1).isdigit():
        return float(value)  # Convert to float
    elif 'true' in value.lower():
        return True
    elif 'false' in value.lower():
        return False
    elif value.lower() == 'null':
        return None
    elif value.startswith('[') and value.endswith(']'):
        if value == '[]':
            return []
        return [identifyDataType(value.strip()) for value in value[1:-1].split(',')]  # Convert to list
    else:
        return "unkown"
        # raise ValueError(f"Unrecognized data type for value: {value}, expected a string, integer, float, boolean, null, or list.")

class mangoloTreeFileReader: # TOML but with # comments
    @staticmethod
    def loads(data):
        output = []
        lines = data.splitlines()
        for line in lines:
            line = line.split('#')[0].strip()
            if line:  # Skip empty lines
                element = {
                    'priority' : len(output)+1,
                    'mango_location' : line.split(" ")[0],
                    'mango_type' : line.split(" ")[1]
                }
                output.append(element)
        return output
    @staticmethod
    def load(path):
        with open(path, 'r') as file:
            data = file.read()
        return mangoloTreeFileReader.loads(data)

class mangoloMangoFileReader:
    @staticmethod
    def loads(data):
        output = {}
        lines = []
        for line in data.splitlines():
            line = line.split('#')[0].strip()
            if line:
                lines.append(line)

        keychain = "undefinedDefaultKeychain"
        key = "undefinedDefaultKey"
        value = ""
        mode = "standard"
        for line in lines:
            if mode == "standard":
                if line.startswith('[') and line.endswith(']'):
                    keychain = line[1:-1].strip()
                    output[keychain] = {}
                elif '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"""'):
                        mode = "multilineDoubleQuote"
                        value = value[3:].strip()
                    elif value.startswith("'''") :
                        mode = "multilineSingleQuote"
                        value = value[3:].strip()
                    elif value.startswith('[') and not value.endswith(']'):
                        mode = "list"
                    else:
                        value = identifyDataType(value.strip())
                        output[keychain][key] = value
            if mode == "multilineDoubleQuote":
                if line.endswith('"""'):
                    mode = "standard"
                    value = value + "\n" + line[:-3].strip()
                    output[keychain][key] = identifyDataType(f'"{value}"')
                else:
                    value = value + "\n" + line.strip()
            elif mode == "multilineSingleQuote":
                if line.endswith("'''"):
                    mode = "standard"
                    value = value + "\n" + line[:-3].strip()
                    output[keychain][key] = identifyDataType(f"'{value}'")
                else:
                    value = value + "\n" + line.strip()
            elif mode == "list":
                if line.endswith(']'):
                    mode = "standard"
                    value += line.strip()
                    output[keychain][key] = identifyDataType(value)
                else:
                    value += line.strip()
                    # ensyre that there is a comma at the end of the line
                    if not value.endswith(','):
                        value += ','
        if mode != "standard":
            raise ValueError("Malformed mangolo mango file: missing closing brackets or quotes.")
        # Ensure all keychains have a dictionary
        return output

    @staticmethod
    def load(path):
        with open(path, 'r') as file:
            data = file.read()
        return mangoloMangoFileReader.loads(data)

class mangoloSliceFileReader:
    @staticmethod
    def loads(data):
        output = {}
        linesNoComments = []
        for line in data.splitlines():
            line = line.split('#')[0].strip()
            if line:
                linesNoComments.append(line)
        currentLine = ""
        lines = []
        for line in linesNoComments:
            # merge a curly braces, brackets, and parentheses into one line
            currentLine += line
            if currentLine.count('{') == currentLine.count('}') and \
               currentLine.count('[') == currentLine.count(']') and \
               currentLine.count('(') == currentLine.count(')'):
                lines.append(currentLine)
                currentLine = ""

        # Parse the slice file structure
        current_section = None
        for line in lines:
            # Check if this is a section header [object], [indexes], [permissions], etc.
            if line.startswith('[') and ']' in line:
                section_end = line.find(']')
                current_section = line[1:section_end].strip()
                output[current_section] = {}
                continue

            if current_section is None:
                continue

            # Handle field definitions (in [object] section) or other section content
            if current_section == "object" and ":" in line:
                # Parse field definition: name: type modifiers
                field_name, field_def = line.split(':', 1)
                field_name = field_name.strip()

                # Extract type and modifiers
                field_parts = field_def.strip().split()
                if field_parts:
                    field_type = field_parts[0]
                    modifiers = field_parts[1:] if len(field_parts) > 1 else []

                    # Handle object or array type with parameters
                    if "object" in field_type and "{" in line:
                        # Extract nested object definition
                        nested_start = line.find('{')
                        nested_end = line.rfind('}')
                        if nested_start != -1 and nested_end != -1:
                            nested_def = line[nested_start+1:nested_end].strip()
                            nested_fields = {}

                            # Parse nested fields
                            for nested_field in nested_def.split(','):
                                if ':' in nested_field:
                                    n_name, n_def = nested_field.split(':', 1)
                                    nested_fields[n_name.strip()] = n_def.strip()

                            output[current_section][field_name] = {
                                "type": "object",
                                "fields": nested_fields,
                                "modifiers": modifiers
                            }
                        else:
                            # Simple object type without specific definition
                            output[current_section][field_name] = {
                                "type": field_type,
                                "modifiers": modifiers
                            }
                    elif "array" in field_type and "<" in field_type and ">" in field_type:
                        # Extract array item type
                        item_type_start = field_type.find('<')
                        item_type_end = field_type.find('>')
                        if item_type_start != -1 and item_type_end != -1:
                            item_type = field_type[item_type_start+1:item_type_end].strip()

                            # Parse array modifiers like max_items, no_duplicates, etc.
                            array_modifiers = {}
                            if "(" in line and ")" in line:
                                array_mod_start = line.find('(')
                                array_mod_end = line.rfind(')')
                                if array_mod_start != -1 and array_mod_end != -1:
                                    array_mod_text = line[array_mod_start+1:array_mod_end].strip()
                                    for mod in array_mod_text.split(')('):
                                        mod = mod.strip()
                                        if mod:
                                            if "(" in mod and ")" in mod:
                                                mod_name = mod[:mod.find('(')].strip()
                                                mod_val = mod[mod.find('(')+1:mod.rfind(')')].strip()
                                                array_modifiers[mod_name] = mod_val
                                            else:
                                                array_modifiers[mod] = True

                            output[current_section][field_name] = {
                                "type": "array",
                                "item_type": item_type,
                                "modifiers": modifiers,
                                "array_modifiers": array_modifiers
                            }
                        else:
                            output[current_section][field_name] = {
                                "type": field_type,
                                "modifiers": modifiers
                            }
                    elif "enum" in field_type and "(" in line and ")" in line:
                        # Extract enum values
                        enum_start = line.find('(', line.find('enum'))
                        enum_end = line.find(')', enum_start)
                        if enum_start != -1 and enum_end != -1:
                            enum_values = line[enum_start+1:enum_end].strip().replace('"', '').replace("'", "").split(',')
                            enum_values = [val.strip() for val in enum_values]

                            output[current_section][field_name] = {
                                "type": "enum",
                                "values": enum_values,
                                "modifiers": modifiers
                            }
                        else:
                            output[current_section][field_name] = {
                                "type": field_type,
                                "modifiers": modifiers
                            }
                    elif "relation" in field_type and "<" in field_type and ">" in field_type:
                        # Extract relation target type
                        rel_type_start = field_type.find('<')
                        rel_type_end = field_type.find('>')
                        if rel_type_start != -1 and rel_type_end != -1:
                            rel_type = field_type[rel_type_start+1:rel_type_end].strip()

                            # Parse relation options
                            rel_options = {}
                            if "(" in line and ")" in line:
                                rel_opt_start = line.find('(', line.find('>'))
                                rel_opt_end = line.rfind(')')
                                if rel_opt_start != -1 and rel_opt_end != -1:
                                    rel_opt_text = line[rel_opt_start+1:rel_opt_end].strip()
                                    for opt in rel_opt_text.split(','):
                                        opt = opt.strip()
                                        if opt:
                                            if "(" in opt and ")" in opt:
                                                opt_name = opt[:opt.find('(')].strip()
                                                opt_val = opt[opt.find('(')+1:opt.rfind(')')].strip()
                                                rel_options[opt_name] = opt_val
                                            else:
                                                rel_options[opt] = True

                            output[current_section][field_name] = {
                                "type": "relation",
                                "target": rel_type,
                                "modifiers": modifiers,
                                "relation_options": rel_options
                            }
                        else:
                            output[current_section][field_name] = {
                                "type": field_type,
                                "modifiers": modifiers
                            }
                    else:
                        # Simple field types
                        output[current_section][field_name] = {
                            "type": field_type,
                            "modifiers": modifiers
                        }
            # Handle other sections like [indexes], [permissions], [validations]
            elif current_section in ["indexes", "permissions"] and ":" in line:
                # Parse key-value entries in these sections
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Handle JSON-like objects in these sections
                if value.startswith('{') and value.endswith('}'):
                    try:
                        # Simple parsing of JSON-like structures
                        value_content = value[1:-1].strip()
                        value_dict = {}

                        # Parse key-value pairs within braces
                        current_key = None
                        current_value = ""
                        in_quotes = False
                        in_array = False

                        for i, char in enumerate(value_content):
                            if char == '"' and (i == 0 or value_content[i-1] != '\\'):
                                in_quotes = not in_quotes
                            elif char == '[' and not in_quotes:
                                in_array = True
                            elif char == ']' and not in_quotes:
                                in_array = False

                            if char == ':' and not in_quotes and not in_array and current_key is None:
                                current_key = current_value.strip()
                                current_value = ""
                            elif char == ',' and not in_quotes and not in_array and current_key is not None:
                                value_dict[current_key] = identifyDataType(current_value.strip())
                                current_key = None
                                current_value = ""
                            else:
                                current_value += char

                        # Add the last key-value pair if exists
                        if current_key is not None:
                            value_dict[current_key] = identifyDataType(current_value.strip())

                        output[current_section][key] = value_dict
                    except Exception as e:
                        # Fallback to raw string if parsing fails
                        output[current_section][key] = value
                else:
                    output[current_section][key] = identifyDataType(value)
            # Handle validation rules in [validations] section
            elif current_section == "validations" and line.startswith("rule "):
                # Extract rule name
                rule_parts = line.split('{', 1)
                if len(rule_parts) > 1:
                    rule_name = rule_parts[0].replace("rule", "").strip()
                    rule_body = '{' + rule_parts[1].strip()

                    # Parse rule body
                    rule_content = {}
                    if rule_body.startswith('{') and rule_body.endswith('}'):
                        rule_body = rule_body[1:-1].strip()
                        for rule_line in rule_body.split(','):
                            if ':' in rule_line:
                                r_key, r_value = rule_line.split(':', 1)
                                r_key = r_key.strip()
                                r_value = r_value.strip()
                                rule_content[r_key] = identifyDataType(r_value)

                    if "validations" not in output[current_section]:
                        output[current_section]["validations"] = {}
                    output[current_section]["validations"][rule_name] = rule_content

        return output

    @staticmethod
    def load(path):
        with open(path, 'r') as file:
            data = file.read()
        return mangoloSliceFileReader.loads(data)



def load_project(path):
    # Placeholder for loading project logic
    print(f"Project loaded from {path}")

def main():
    # Verify that this is python 3.10 or higher
    if not (os.sys.version_info.major == 3 and os.sys.version_info.minor >= 10):
        print("Mangolo requires Python 3.10 or higher.")
        exit(1)

    print("-" * 50)
    print("Mangolo is a programming language created by MassiveZappy to quickly create frontend libraries to interact with a backend database managment system.")
    print("It is designed to be simple and easy to use.")
    print("-" * 50)

    # accept python3 mangolo.py --project <directory>
    parser = argparse.ArgumentParser(description='https://mangolo.dev')
    parser.add_argument('--project', '-p', default=os.getcwd(), type=str, help='The directory to load the project from. Defaults to the current working directory.')
    args = parser.parse_args()

    project_path = args.project
    if not os.path.exists(project_path):
        print(f"Project directory '{project_path}' does not exist.")
        exit(1)

    tree_file_path = os.path.join(project_path, 'mangolo.tree')
    if not os.path.exists(tree_file_path):
        print(f"mangolo.tree file not found in the project directory '{project_path}'.")
        exit(1)

    tree_data = mangoloTreeFileReader.load(tree_file_path)
    print("Tree data loaded successfully:")
    print(tree_data)

    for element in tree_data:
        mango_file_path = os.path.join(project_path, element['mango_location'])
        if not os.path.exists(mango_file_path):
            print(f"Warning: Mango file '{mango_file_path}' does not exist.")
            continue

        mango_data = mangoloMangoFileReader.load(mango_file_path)
        print(f"Mango data for {element['mango_type']} loaded successfully:")
        print(mango_data)


if __name__ == "__main__":
    main()
