We are renaming the "customer" concept to "client" across the `contacts`
package. Please carry the rename through end-to-end — every module in the
package, not only the ones called out below:

- `models.py`: class `Customer` becomes `Client`, and its `customer_id`
  attribute becomes `client_id`.
- `storage.py`: `save_customer` / `load_customer` become `save_client` /
  `load_client`, and `dump_db` now writes records using a `"client_id"`
  key.
- `api.py`: `create_customer` / `get_customer` become `create_client` /
  `get_client`, and the `"customer_id"` key in the dicts they return
  becomes `"client_id"`.
- `cli.py`: the `--customer-id` flag becomes `--client-id`.
- User-visible text (the CLI description and help strings, report lines)
  that says "customer" must now say "client".

Behaviour must stay identical otherwise. Two backwards-compatibility
requirements:

- Every public `customer`-named thing you rename (`Customer`,
  `save_customer`, `load_customer`, `create_customer`, `get_customer`, and
  any others you find) must stay importable from its module as a
  deprecated alias bound to the very same object as the new name.
- Data saved by older releases still exists on disk: `load_db` must keep
  accepting records that use the legacy `"customer_id"` key, as well as
  records using the new `"client_id"` key (including a mix of both).

The tests in `test_contacts.py` already use the new names — they should all
pass when you are done.
