import pytest
from tests.helpers.inspect_tests import check_duplicate_test_names
import os
import sys


root_path = os.path.dirname(os.path.abspath(__file__))

if root_path not in sys.path:
    sys.path.append(root_path)


def pytest_configure():
    def add_package_path(package_name: str):
        package_root = os.path.join(root_path, package_name)

        if package_root not in sys.path:
            sys.path.append(package_root)

    pytest.add_robin_package_path = add_package_path

# Test report - add info about test ids:
def pytest_collection_modifyitems(session, config, items):
    modules_seen = set()
    duplicate_defs_by_modules = dict()

    for item in items:

        # Check duplicate names of tests:
        mod_path, line, test_name = item.location

        print(f'collecting: "{test_name}" in "{mod_path}", at #{line}')

        if mod_path not in modules_seen:
            modules_seen.add(mod_path)
            # New module...
            duplicates = check_duplicate_test_names(item.module)
            if duplicates:
                duplicate_defs_by_modules[mod_path] = duplicates

        # Collect names:
        for marker in item.iter_markers(name="test_case_name"):
            test_case_name = marker.args[0] if len(marker.args) > 0 else f'Забыли имя кейса! {item}'
            item.user_properties.append(("test_case_name", test_case_name))
        #Collect IDs:
        for marker in item.iter_markers(name="test_case_id"):
            test_case_id = marker.args[0] if len(marker.args) > 0 else f'Забыли ID кейса! {item}'
            item.user_properties.append(("test_case_id", test_case_id))
    
    # If duplicates found: print report and stop tests
    if duplicate_defs_by_modules:
        buff = []
        mod_count = 0
        dup_count = 0
        # Make error report:
        for mod_path, duplicates in duplicate_defs_by_modules.items():
            serialized = ', '.join(duplicates)
            buff.append(f'multiple definitions in "{mod_path}" with names: "{serialized}"')
            mod_count += 1
            dup_count += len(duplicates)

        print()
        print('*** Errors: non-uniques names of tests! ***')
        for line in buff:
            print(line)
        raise pytest.UsageError(f'Test name duplicates in same module: {dup_count} cases in {mod_count} modules')

        
