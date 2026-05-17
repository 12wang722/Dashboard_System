CREATE_USER_CASES = {
    "valid_user": {
        "payload": {
            "name": "autotest-user",
            "email": "autotest@example.com"
        },
        "expected_status": 201,
        "expected_code": 0,
    },
    "missing_email": {
        "payload": {
            "name": "autotest-user"
        },
        "expected_status": 400,
        "expected_code": 1001,
    },
    "invalid_email": {
        "payload": {
            "name": "autotest-user",
            "email": "bad-format"
        },
        "expected_status": 400,
        "expected_code": 1002,
    },
}
