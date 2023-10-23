#!/usr/bin/env python3

import json
import sys

def json_validator(data):
    try:
        json.loads(data)
        return True
    except ValueError as error:
        print(f"invalid json: {error}")
        return False

def test_json_validator(abi_name):
    with open(abi_name,'r') as abi_file:
        abi_text = abi_file.read()
    return json_validator(abi_text)

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        print("Testing abi file ", filename)
        if not test_json_validator(filename):
            exit(1)
    exit(0)
