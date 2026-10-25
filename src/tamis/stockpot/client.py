import httpx
from pydantic import BaseModel


class GetToken(BaseModel):
    token: str


class GetUser(BaseModel):
    id: int
    name: str


class Client:
    def __init__(self, host: str) -> None:
        self.host = host

    def get_token(self, username: str, password: str) -> str:
        resp = httpx.post(
            f"{self.host}/user/token",
            auth=httpx.BasicAuth(username=username, password=password),
        )
        resp.raise_for_status()

        return GetToken.model_validate(resp.json()).token

    def validate_token(self, token: str) -> tuple[bool, GetUser | None]:
        resp = httpx.get(
            f"{self.host}/user/auth",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == httpx.codes.UNAUTHORIZED:
            return False, None
        resp.raise_for_status()
        return True, GetUser.model_validate(resp.json())
