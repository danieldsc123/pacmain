# Validation record

Executed on 2026-11-07, Linux, Python 3.13.1.

- Mandatory flake8 and mypy flags: passed, nine source files checked.
- Strict mypy: passed for the final nine source files, including all six tests.
- Six unittest acceptance cases: passed against the real assigned wheel.
- Native PyInstaller build and ZIP generation: passed (approximately 25 MB ZIP).
- Packaged executable with no argument: clean usage message, exit status 2.
- Packaged executable with config: clean display connection error, exit status 1,
  without traceback. This confirms startup handling, not graphical correctness.
- Original wheel SHA-256:
  `98e12f7e989cef03dd4411657d7bee12653804aee87a568eddfaf21436ffd4aa`.

A runtime annotation compatibility issue (`tk.Event` subscription) was found on
startup and fixed by postponing annotation evaluation. The package was rebuilt
after this fix.

Graphical screen smoke testing was attempted but cannot run because the available
environment cannot connect to display `:0`. No successful GUI playthrough, visual
inspection, clean-machine test or platform deployment is claimed. Follow the
manual acceptance plan in PLAN.md on an actual graphical desktop.
