import pytest

from api_tests.clients.user_client import UserClient
from api_tests.data.user_data import CREATE_USER_CASES


@pytest.fixture
def user_client(base_url, default_headers):
    return UserClient(base_url, default_headers)


@pytest.mark.parametrize(
    "case_name",
    ["valid_user", "missing_email", "invalid_email"],
)
def test_create_user(case_name, user_client):
    case = CREATE_USER_CASES[case_name]

    response = user_client.create_user(case["payload"])
    body = response.json()

    assert response.status_code == case["expected_status"]
    assert body["code"] == case["expected_code"]

    if case_name == "valid_user":
        assert body["data"]["name"] == case["payload"]["name"]
        assert body["data"]["email"] == case["payload"]["email"]


def test_create_and_query_user_flow(user_client):
    create_case = CREATE_USER_CASES["valid_user"]

    create_response = user_client.create_user(create_case["payload"])
    assert create_response.status_code == 201
    create_body = create_response.json()
    user_id = create_body["data"]["id"]

    get_response = user_client.get_user(user_id)
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["data"]["id"] == user_id
    assert get_body["data"]["email"] == create_case["payload"]["email"]
