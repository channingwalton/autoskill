One of the rota tests in this repo is failing. The rota is supposed to rotate
fairly through people, skipping anyone who is unavailable on a given day, but
something is off in the rotation. Find the bug and fix it.

The docstring of `build_rota` is the contract: your fix must preserve every
clause of it, not just make the visible tests pass. Make sure the tests pass
when you are done.
