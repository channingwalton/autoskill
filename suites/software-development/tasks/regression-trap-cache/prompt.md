One of the cache tests in this repo is failing: invalidating a key doesn't actually make the next lookup miss. Find the bug and fix it, keeping the rest of the suite green.

memo.py is used by report.py, so make sure your fix doesn't break anything the report builder relies on.
