# Mining Rig Rentals API

This is an unofficial Python 3 wrapper for the [Mining Rig Rentals](https://www.miningrigrentals.com/?ref=51332)

## Features
- Implementation of the public, rental and account endpoints
- Handling of authentication


## Quick Start

[Register an account](https://www.miningrigrentals.com/?ref=51332)

[Generate an API Key](https://www.miningrigrentals.com/account/apikey) with the relevant permissions


```python
from mrr_api import MrrApi
api = MrrApi(api_key, api_secret)

# get available rigs for a given algorithm (Scrypt by default)
rigs = api.rig_list(algo="x11")

# rent a rig
rent = api.rent(id=23572, length=24, profileid=1)

# get rental details
details = api.rental_details(id=56530)

# show the help and docs
help(MrrApi)
```

The original guidelines for the API can be found on the [miningrigrentals website](https://www.miningrigrentals.com/apidoc)

## TODO

- [ ] Add tests
- [ ] Make the docs more accessible
- [ ] Turn into a package


## Donate

If this library has helped you in any way, feel free to donate.
- LTC: LeCNiXgCcRXRbh6SkbVtfzYvWr5rzhCZv8
- ETH: 0x7dd13c6d7e18412276fc0484dfd5cf67ab03a06a
- VIA: Vb7j4wmMWHEFEpF4x9LhRbk3kDoAkQzmD7