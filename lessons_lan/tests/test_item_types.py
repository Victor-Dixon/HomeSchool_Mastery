from app.grading import grade_multi_select, grade_ordering, grade_short_response


def test_multi_select_exact_match():
    assert grade_multi_select(["a", "b"], ["b", "a"]) is True
    assert grade_multi_select(["a"], ["a", "b"]) is False
    assert grade_multi_select(["a", "c"], ["a", "b"]) is False


def test_ordering_requires_exact_order():
    assert grade_ordering(["1", "2", "3"], ["1", "2", "3"]) is True
    assert grade_ordering(["2", "1", "3"], ["1", "2", "3"]) is False


def test_short_response_normalization():
    assert grade_short_response(" 3/10 ", "3/10") is True
    assert grade_short_response("It is about to rain", ["it is about to rain", "rain is coming"]) is True
    assert grade_short_response("wrong", "3/10") is False
