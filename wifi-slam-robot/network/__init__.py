import requests


def send_request(request: dict, address: str, port: int) -> dict:
    response = requests.post(f'http://{address}:{port}/', json=request)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None
