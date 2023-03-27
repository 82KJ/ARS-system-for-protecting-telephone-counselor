import requests

resp = requests.post(
    'https://openapi.vito.ai/v1/authenticate',
    data={'client_id': 'NFJOMvUAYfhQiZA8ZQit',
          'client_secret': 'XJ2pgsDOaR8RilnUjvHKwaF9_WbXVjwcsfPMHx5L'}
)
resp.raise_for_status()
print(resp.json())