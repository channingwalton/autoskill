We are renaming the "customer" concept to "client" across the `contacts`
package. Please carry the rename through end-to-end:

- `models.py`: class `Customer` becomes `Client`, and its `customer_id`
  attribute becomes `client_id`.
- `storage.py`: `save_customer` / `load_customer` become `save_client` /
  `load_client`.
- `api.py`: `create_customer` / `get_customer` become `create_client` /
  `get_client`, and the `"customer_id"` key in the dicts they return
  becomes `"client_id"`.
- `cli.py`: the `--customer-id` flag becomes `--client-id`.

Behaviour must stay identical otherwise. For backwards compatibility, keep
the old names (`Customer`, `save_customer`, `load_customer`,
`create_customer`, `get_customer`) importable from their modules as
deprecated aliases of the new ones.

The tests in `test_contacts.py` already use the new names — they should all
pass when you are done.
