
from extraction.json_recognizer import recognize_json


def test_assignment():
    data = {
        "id": "7985516",
        "due_at": None,
        "graded": True,
        "overrides": []
    }

    assert recognize_json(data) == ["assignment"]


def test_assignment_without_id():
    data = {
        "due_at": None,
        "graded": True,
        "overrides": []
    }

    assert recognize_json(data) == ["assignment"]


def test_module():
    data = [
        {
            "id": "3055756",
            "name": "Test Module",
            "published": True,
            "items_count": 5,
            "items_url": "/modules/3055756/items"
        }
    ]

    assert recognize_json(data) == ["module"]


def test_module_without_id():
    data = {
        "items_count": 5,
        "items_url": "/modules/1/items"
    }

    assert recognize_json(data) == ["module"]


def test_navigation():
    data = {
        "items": [
            {
                "current": {"id": "21408224"},
                "prev": None,
                "next": None
            }
        ],
        "modules": [{"id": "3141272"}]
    }

    assert recognize_json(data) == ["navigation"]


def test_configuration():
    data = {
        "lmsType": "Canvas",
        "flags": {},
        "academicYearStart": 1441065600000
    }

    assert recognize_json(data) == ["configuration"]


def test_nested_assignment():
    data = {
        "response": {
            "data": {
                "id": "7985516",
                "due_at": None,
                "graded": True
            }
        }
    }

    assert recognize_json(data) == ["assignment"]


def test_combined_response():
    data = {
        "response": {
            "assignment": {
                "due_at": None,
                "graded": True
            },
            "module": {
                "items_count": 5,
                "items_url": "/modules/1/items"
            }
        }
    }

    result = recognize_json(data)

    assert set(result) == {"assignment", "module"}


def test_unknown_json():
    data = {
        "message": "Hello",
        "status": "success"
    }

    assert recognize_json(data) == ["unknown"]


def test_invalid_input():
    assert recognize_json(None) == ["unknown"]
    assert recognize_json("Canvas") == ["unknown"]


def test_large_array():
    data = [
        {
            "id": i,
            "items_count": 5,
            "items_url": f"/modules/{i}/items"
        }
        for i in range(5000)
    ]

    assert recognize_json(data) == ["module"]


if __name__ == "__main__":
    tests = [
        test_assignment,
        test_assignment_without_id,
        test_module,
        test_module_without_id,
        test_navigation,
        test_configuration,
        test_nested_assignment,
        test_combined_response,
        test_unknown_json,
        test_invalid_input,
        test_large_array
    ]

    for test in tests:
        test()
        print(f"PASSED: {test.__name__}")

    print("\nAll recognizer tests passed!")
