"""
Originally extracted from these functions:

$ npm_email="$(http GET "https://registry.npmjs.org/-/user/org.couchdb.user:$github_user" | jq -r '.email | select( . != null )')"
$ http https://pypi.org/pypi/$project_name/json | jq -r '.info.author_email'

# maybe use tools here
https://cookbook.openai.com/examples/using_tool_required_for_customer_service
"""

from decouple import config
from pydantic import BaseModel

from models import ContactInfo
from utils import log


def extract_email_from_name_and_email_string(author_info: str) -> tuple[str, str]:
    """
    Extract name and email from email string like:

    Melnor Customer Service <mcustomer@melnor.com>.
    """
    import re

    if author_info:
        match = re.match(r"(.*?)\s*<(.+?)>", author_info)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    return "", author_info.strip()


def _make_npm_request(url: str) -> dict:
    """Make authenticated request to NPM registry."""
    import requests

    npm_token = config("NPM_TOKEN", cast=str)
    headers = {"Authorization": f"Bearer {npm_token}"} if npm_token else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {}


def get_npm_package_info(package_name: str) -> dict:
    """
       Get package metadata from NPM registry. Here's an example response.

       {'_id': 'lunch-money',
    '_rev': '4-d732d45d0b15bb33932f3027d386c037',
    'name': 'lunch-money',
    'dist-tags': {'latest': '0.5.0'},
    'versions': {'0.0.1': {'name': 'lunch-money',
      'version': '0.0.1',
      'description': '## Installing',
      'main': 'dist/index.js',
      'scripts': {'test': 'echo "Error: no test specified" && exit 1',
       'build': 'tsc'},
      'repository': {'type': 'git',
       'url': 'git+ssh://git@github.com/lunch-money/lunch-money-js.git'},
      'keywords': ['lunch-money', 'lunchmoney'],
      'author': {'name': 'Joe Hoyle'},
      'license': 'MIT',
      'bugs': {'url': 'https://github.com/lunch-money/lunch-money-js/issues'},
      'homepage': 'https://github.com/lunch-money/lunch-money-js#readme',
      'devDependencies': {'@types/isomorphic-fetch': '^0.0.35',
       '@types/node': '^13.9.3',
       'typescript': '^3.8.3'},
      'types': 'dist/index.d.ts',
      'dependencies': {'isomorphic-fetch': '^2.2.1'},
      'gitHead': '4c99f2128513a45815db6b9539b12479645d63d3',
      '_id': 'lunch-money@0.0.1',
      '_nodeVersion': '10.19.0',
      '_npmVersion': '6.13.4',
      'dist': {'integrity': 'sha512-ZLWaZ9IW7qIVc1KE8jFhvh+wT0E1eeH7LoUpVss2u/H9OCf+k8euyh+qegYhMsYuAy9wfBB7ZzltDZoN8g318w==',
       'shasum': '6768e304c82228456beea4ffbc98da779f4c4ec7',
       'tarball': 'https://registry.npmjs.org/lunch-money/-/lunch-money-0.0.1.tgz',
       'fileCount': 6,
       'unpackedSize': 15421,
       'npm-signature': '-----BEGIN PGP SIGNATURE-----\r\nVersion: OpenPGP.js v3.0.4\r\nComment: https://openpgpjs.org\r\n\r\nwsFcBAEBCAAQBQJefO/sCRA9TVsSAnZWagAAteMP/2F79tE3xDKalRx0KCko\nF/HMMSQCzUQS86p3BUqifG9MQlbzi932HXij2L6d9R1bcbEUiuYBITLjUVpx\nHQZAoaaacgahs8pu+QPY0MA8p/K5GUQJ6cG92SMEZkuE9pMgvB+IjP2gEWKM\nhB0bipjG7DO/6S54J8QLlRw7FPqX6oCN0AHAXYU/glDBW+blEX0xblnchQCH\nIV+CHW3n8szohU/+4ThRxxTSb02wLLbgTw/0gB1XMcaEs6aaQb09bryUnh7a\nOtx00vX7y1RUL8AOOVp4Q99X+wC/d0yosm+PFGr46DLp1/8mPA6d4R4avZXf\n7YP7/ICs3ODVpHuDNuP+uUiMi4tAyxBBVLdT0RRGnVIaIlxWNQmHTriFdsHz\nzEE5K6PmRa3f4cjc+USwhJhnuk9nGUU0bH5pzqFmwIFn5wgx9ghpjJni7Sww\nmP+9E8FiJuzAGZEnu/7YUVh5vM/+W6z6B/Lg2mRbZJFjRQxsulEJqogwKS8e\ngKhgv6sqwCbXMHfc6iX4QlODfxLlbgCYWN3k70EmUMkYb63BfzJTp/6ooxDz\nLXJ7kCXrs0IZUDdsHlOci0GOHkG0JMcoU7Hu8iZiX3hEicKe4VIAxDzQExZ8\nZI+U7fau/ns1TO8Oa1mXkq90e0WWdLmgw1MIN9YNkhn8VgmQ/yUTNRR7POpL\nr4kH\r\n=Jp8n\r\n-----END PGP SIGNATURE-----\r\n',
       'signatures': [{'keyid': 'SHA256:jl3bwswu80PjjokCgh0o2w5c2U4LhQAE57gj9cz1kzA',
         'sig': 'MEYCIQCRBwv4zjZjtkouQIfUjqIBqM33LPIBL9TCtLFpyGZ8xAIhAOoeCzJUxBRaTkKJ+ON/AcFRlgo1c8w0K+3ua8MCKYrg'}]},
      'maintainers': [{'name': 'joehoyle', 'email': 'joehoyle@gmail.com'}],
      '_npmUser': {'name': 'joehoyle', 'email': 'joehoyle@gmail.com'},
      'directories': {},
      '_npmOperationalInternal': {'host': 's3://npm-registry-packages',
       'tmp': 'tmp/lunch-money_0.0.1_1585246187855_0.08019073300201018'},
      '_hasShrinkwrap': False},
     '0.5.0': {'name': 'lunch-money',
      'version': '0.5.0',
      'description': 'API bindings for the Lunch Money personal finance application',
      'type': 'commonjs',
      'main': 'dist/index.js',
      'scripts': {'test': 'echo "Error: no test specified" && exit 1',
       'build': 'tsc'},
      'repository': {'type': 'git',
       'url': 'git+ssh://git@github.com/lunch-money/lunch-money-js.git'},
      'keywords': ['lunch-money', 'lunchmoney'],
      'author': {'name': 'Joe Hoyle'},
      'contributors': [{'name': 'Michael Bianco',
        'email': 'mike@mikebian.co',
        'url': 'https://mikebian.co/about'}],
      'license': 'MIT',
      'bugs': {'url': 'https://github.com/lunch-money/lunch-money-js/issues'},
      'homepage': 'https://github.com/lunch-money/lunch-money-js#readme',
      'devDependencies': {'@types/isomorphic-fetch': '^0.0.35',
       '@types/node': '^16.11.0',
       'typescript': '^4.4.4'},
      'types': 'dist/index.d.ts',
      'dependencies': {'isomorphic-fetch': '^3.0.0'},
      'gitHead': '3c48c7c316c9b8162f6723627af9dade6c9cf7a6',
      '_id': 'lunch-money@0.5.0',
      '_nodeVersion': '16.11.0',
      '_npmVersion': '8.5.4',
      'dist': {'integrity': 'sha512-GcsaFTZdK1rLGmu/fcA0fsIibTrY5PRuelmoXUx23R+yFGaBQc+HUDkthiKjh929YM9C9Cs8LxTKxN576yXMvg==',
       'shasum': 'f5c1d8e15532871cc1ad768d5d139caaa1d6425f',
       'tarball': 'https://registry.npmjs.org/lunch-money/-/lunch-money-0.5.0.tgz',
       'fileCount': 6,
       'unpackedSize': 22889,
       'signatures': [{'keyid': 'SHA256:jl3bwswu80PjjokCgh0o2w5c2U4LhQAE57gj9cz1kzA',
         'sig': 'MEUCIQCcp03aeE9Pyzs9l/NFo8YDJZ9U4PZ78dhy7/nQKPNOsQIgJAArW5dutxr66D9H+44NZqZE+AawUO8YBiPflaA7pX0='}],
       'npm-signature': '-----BEGIN PGP SIGNATURE-----\r\nVersion: OpenPGP.js v4.10.10\r\nComment: https://openpgpjs.org\r\n\r\nwsFzBAEBCAAGBQJimLMOACEJED1NWxICdlZqFiEECWMYAoorWMhJKdjhPU1b\r\nEgJ2VmrWEg//ZdVRnky1f8C0BcJFh5LmE/NhjfT9buhd4jBCFyMuO4AbSmty\r\nFnjE9SrJ77cXuwDIaTXmsal1/7DpkYi8lbFL2nPit1IuKlEmjLg1XADKhkar\r\n7iOclZmyihbuJ+cOazTKtABiHrd3BarYbN8X7+3miZay9ipuSoQaGDMYHB+i\r\nfYX7KSRqIoIm4hFgmpXec8JPpoNbAmYJA5YgLeTa94x9rBRvMKJ9fu8B55dS\r\nxn9LalVB7rFHz0uEpY9cubleX7cEnMcaVnQbziVDddEckLrzrQ4UI3b+nU4S\r\nesRI0P5BFykFqPjWMENJVxUydUgMR0AchQlTClappKqNTRMqLOUgUjSX3agO\r\nEIiMPLEGyMZdLPBr07Kr7bw2Bw9QOm5FAkvbIsyTgx5M4EaKNynKDm0/yuUW\r\nc2ZpoV4JsCzg7+6uf/v3+RlA33t550Fk5bYBK2HKHhc5nT6sqx8rFal9WSgh\r\n4ACYo8b//XZXVAtyT+eIWeo5xdIZJGIAiUqUMl9vV7Ny6VPlbL6GCBVMyJ0U\r\n7yD0Cr27D8Dq1vR681k88r8ZLn3Vif6U7cVcEYvIAjOfoKgbbAy4flASn5dR\r\nOE77aLjvJiku1+Jrp82WZpSHK8argH//aczNaY5MH/3YiCnOHp+uktf1U3vQ\r\ndBHVyHcLsbPkq93JRMxXQsjnpISA8kHeIZI=\r\n=qLDf\r\n-----END PGP SIGNATURE-----\r\n'},
      '_npmUser': {'name': 'iloveitaly', 'email': 'mike@mikebian.co'},
      'directories': {},
      'maintainers': [{'name': 'joehoyle', 'email': 'joehoyle@gmail.com'},
       {'name': 'iloveitaly', 'email': 'mike@mikebian.co'}],
      '_npmOperationalInternal': {'host': 's3://npm-registry-packages',
       'tmp': 'tmp/lunch-money_0.5.0_1654174478099_0.42236742079280765'},
      '_hasShrinkwrap': False}},
    'time': {'created': '2020-03-26T18:09:47.855Z',
     '0.0.1': '2020-03-26T18:09:48.007Z',
     'modified': '2022-06-07T15:55:31.124Z',
     '0.5.0': '2022-06-02T12:54:38.301Z'},
    'maintainers': [{'email': 'joehoyle@gmail.com', 'name': 'joehoyle'},
     {'email': 'lunchbag@gmail.com', 'name': 'lunchbag'},
     {'email': 'mike@mikebian.co', 'name': 'iloveitaly'}],
    'description': 'API bindings for the Lunch Money personal finance application',
    'homepage': 'https://github.com/lunch-money/lunch-money-js#readme',
    'keywords': ['lunch-money', 'lunchmoney'],
    'repository': {'type': 'git',
     'url': 'git+ssh://git@github.com/lunch-money/lunch-money-js.git'},
    'author': {'name': 'Joe Hoyle'},
    'bugs': {'url': 'https://github.com/lunch-money/lunch-money-js/issues'},
    'license': 'MIT',
    'readme': "# Lunch Money JS\n\n## Installing\n\n```\nnpm install lunch-money\n```\n\nThe NPM module also makes types available to TypeScript.\n\n## Usage\n\n```js\nimport LunchMoney, { Asset } from 'lunch-money';\n\nconst lunchMoney = new LunchMoney( { token: 'my-api-token' } );\n\nlunchMoney.getAssets().then( ( assets: Asset[] ) => {\n\tconsole.log( assets )\n} ).catch ( error => {\n\tconsole.error( error );\n} );\n```\n\nOr, if you are using ESM:\n\n```javascript\nimport {LunchMoney} from 'lunch-money'\nconst lunchMoney = new LunchMoney( { token: 'my-api-token' } );\nconst assets = await lunchMoney.getAssets();\n```\n\n## API\n\nGet all assets (manually managed accounts):\n\n```typescript\nLunchMoney.getAssets() : Promise<Asset>\n```\n\nGet all transactions:\n\n```typescript\nLunchMoney.getTransactions( arguments?: TransactionsEndpointArguments ) : Promise<Transaction[]>\n```\n\nCreate transactions\n\n```typescript\nLunchMoney.createTransactions(\n\ttransactions: DraftTransaction[],\n\tapplyRules = false,\n\tcheckForRecurring = false,\n\tdebitAsNegative = false\n) : Promise<any>\n```\n\n## Examples\n\nThere are many open source projects with example code you can use to quickly build your integration:\n\nhttps://lunchmoney.dev/#awesome-projects",
    'readmeFilename': 'README.md',
    'contributors': [{'name': 'Michael Bianco',
      'email': 'mike@mikebian.co',
      'url': 'https://mikebian.co/about'}]}
    """
    url = f"https://registry.npmjs.org/{package_name}"
    return _make_npm_request(url)


def get_npm_contact_info(github_user: str) -> str:
    """Extract contact email from NPM registry for a given GitHub user."""
    url = f"https://registry.npmjs.org/-/user/org.couchdb.user:{github_user}"
    data = _make_npm_request(url)

    return data.get("email", "")


def get_npm_contact_information_from_npm_package(
    package_name: str,
) -> list[ContactInfo]:
    """
    Extract contact email from NPM registry for a given package.

    Args:
        package_name: Name of the npm package
    """

    log.info("npm package request", package_name=package_name)

    package_info = get_npm_package_info(package_name)

    # look at contributors and author fields and see if we can find an email
    contributors = package_info.get("contributors", [])
    maintainers = package_info.get("maintainers", [])
    author = package_info.get("author", {})

    contact_list = []

    # now parse the name and email out from contributors & maintainers
    for contributor in contributors + maintainers:
        if email := contributor.get("email", ""):
            contact_list.append(ContactInfo(email=email))

    if author_email := author.get("email", ""):
        contact_list.append(ContactInfo(email=author_email))

    return contact_list


class PypiPackageResponse(BaseModel):
    "Pypi package contact information"

    package_name: str
    author_name: str
    author_email: str


def get_pypi_contact_info(project_name: str) -> PypiPackageResponse:
    """
    Extract author email from PyPI registry for a given project.

    Args:
        project_name: Name of the pypi project
    """

    log.info("pypi package request", project_name=project_name)

    import requests

    url = f"https://pypi.org/pypi/{project_name}/json"
    response = requests.get(url)
    response.raise_for_status()

    if response.status_code == 200:
        data = response.json()
        author_info = data.get("info", {}).get("author_email", "")
        name, email = extract_email_from_name_and_email_string(author_info)
        return PypiPackageResponse(
            package_name=project_name,
            author_name=name,
            author_email=email,
        )
    else:
        raise ValueError(f"Failed to fetch package info for {project_name}")


def get_npm_package_contacts(package_name: str) -> list[dict[str, str]]:
    data = get_npm_package_info(package_name)
    maintainers = data.get("maintainers", [])
    contacts = []
    for maint in maintainers:
        name = maint.get("name", "")
        email = maint.get("email", "")
        if email:
            contacts.append({"email": email, "name": name})
    return contacts


if __name__ == "__main__":
    # print(get_pypi_contact_info("aiautocommit"))
    # print(get_npm_contact_info("lunch-money"))
    # get_npm_package_info("lunch-money")
    print(get_npm_contact_information_from_npm_package("lunch-money"))
