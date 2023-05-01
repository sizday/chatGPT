import pytest
import os

def requires_env(*envs):

    envs = envs if isinstance(envs, list) else [*envs]

    satisfied = set(envs).issubset(set(os.environ.keys()))

    return pytest.mark.skipif(
        not satisfied,
        reason=f"Not suitable envrionment {envs} for current test"
    )