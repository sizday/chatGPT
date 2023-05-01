import inspect
import re

from typing import List

TEST_PATTERN = r'^\s*\bdef\b\s*([^\()]*).*' # find text like "def myfunc(..."

def check_duplicate_test_names(module) ->  List[str]:
    mod_as_text = inspect.getsource(module)
    found = re.findall(TEST_PATTERN, mod_as_text, re.MULTILINE)
    seen = set()
    duplicates = set()
    for name in found:
        if name in seen:
            duplicates.add(name)
        seen.add(name)
    
    return list(duplicates)

