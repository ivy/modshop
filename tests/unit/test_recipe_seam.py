from modshop.core.recipe import Entry, Step
from modshop.kotor.steps import Copy


def test_a_step_model_is_a_step_and_an_entry_holds_it() -> None:
    step: Step = Copy(src="*/Override")
    entry = Entry(name="x", inputs=("x",), steps=(step,))
    assert entry.all_inputs() == ("x",)
    assert step.canonical()["do"] == "copy"
    assert "src" in step.canonical()
