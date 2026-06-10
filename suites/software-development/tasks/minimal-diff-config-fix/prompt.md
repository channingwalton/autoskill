One test in test_config.py is failing. Fix config.py so the whole suite passes and the parser honours every quoting rule in its module docstring — the docstring is the spec, and not all of it is covered by the visible tests.

Keep the change minimal — this module is shared across several services and is under change control, so reviewers will reject anything beyond a small, focused fix. Do not modify any file other than config.py, do not create any new files, and do not delete any files.
