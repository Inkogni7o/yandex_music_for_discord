from yandex_music import Client, DeviceCode


def show_auth_code(code: DeviceCode) -> None:
    print(f"Open: {code.verification_url}")
    print(f"Enter code: {code.user_code}")
    print("Waiting for authorization...")


def get_token() -> str:
    oauth_token = Client().device_auth(on_code=show_auth_code)
    return oauth_token.access_token


if __name__ == "__main__":
    print(f"YANDEX_TOKEN = {get_token()!r}")
