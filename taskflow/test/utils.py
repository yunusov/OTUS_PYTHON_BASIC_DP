def assert_json_equal(expected: dict, actual: dict, exclude: list[str] | None = None):
    expected_copy = expected.copy()
    actual_copy = actual.copy()

    if exclude:
        for field in exclude:
            expected_copy.pop(field, None)
            actual_copy.pop(field, None)

    assert expected_copy == actual_copy