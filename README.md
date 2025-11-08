# Menubar-Calculator

Lightweight macOS menu-bar calculator. The app is triggered through the status bar and opens a split-view editor for inputs and results. Built using [rumps](https://github.com/jaredks/rumps), the Ridiculously Uncomplicated macOS Python Statusbar framework.

<img width="636" height="293" alt="mb-calc" src="https://github.com/user-attachments/assets/919d8a69-68f6-4ef5-974b-3cd5d065cf05" />

## Development

- Build bytecode: `python -m compileall src`
- Launch locally: `uv run mb-calc` or `briefcase dev`

## Build

This app uses [Briefcase](https://beeware.org/docs/briefcase/) to build the app.

```
briefcase create (only once)
briefcase build (to update)
briefcase package (for dmg)
```

> Briefcase installs `rumps` from the vendored wheel in `vendor/wheels`. Regenerate it with `uv run python -m pip wheel --no-deps --wheel-dir vendor/wheels "rumps==0.4.0"` if you upgrade the dependency.
