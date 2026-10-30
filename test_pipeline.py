from pipeline import clean_to_three_bullets

def test_keeps_only_three_bullets():
    text = "Intro\n- one\n* two\n• three\n- four"
    assert clean_to_three_bullets(text) == "- one\n- two\n- three"

def test_strips_think_block():
    assert clean_to_three_bullets("<think>x</think>\n- a") == "- a"