from mb_calc import main


def test_main_invokes_toolbar_app(monkeypatch) -> None:
    run_called = False

    class DummyApp:
        def run(self) -> None:
            nonlocal run_called
            run_called = True

    monkeypatch.setattr("mb_calc.ToolbarApp", DummyApp)
    main()

    assert run_called
