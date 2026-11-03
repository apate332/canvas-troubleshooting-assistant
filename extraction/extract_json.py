
import json
from extraction.json_recognizer import recognize_json

def repair_truncated_json(text):
    """
    Attempt to repair JSON that is missing closing braces or brackets.

    This only restores structural closing characters.
    It does not invent missing values or modify Canvas data.
    """

    if not isinstance(text, str):
        return text

    text = text.strip()

    if not text:
        return text

    stack = []
    in_string = False
    escaped = False

    for char in text:

        # Handle characters inside JSON strings.
        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == '"':
                in_string = False

            continue

        # Enter a JSON string.
        if char == '"':
            in_string = True
            continue

        # Track opening structures.
        if char == "{":
            stack.append("}")

        elif char == "[":
            stack.append("]")

        # Remove structures that were properly closed.
        elif char in ("}", "]"):

            if stack and char == stack[-1]:
                stack.pop()

            else:
                # Mismatched structure.
                return text

    # Do not attempt to repair an unfinished string.
    if in_string:
        return text

    # Close any structures that remained open.
    while stack:
        text += stack.pop()

    return text

def load_json(source):
    """
    Read JSON from a file path, uploaded file,
    or an already-parsed Python dictionary/list.
    """

    # Handle already-parsed JSON data.
    if isinstance(source, (dict, list)):
        return source

    # Handle Streamlit UploadedFile or another file-like object.
    if hasattr(source, "read"):
        source.seek(0)
        data = json.load(source)
        source.seek(0)
        return data

    # Handle a regular file path.
    with open(source, "r", encoding="utf-8") as file:
        return json.load(file)



def find_nested_objects(data, max_objects=10000, max_depth=50):
    """
    Find dictionaries inside nested JSON objects and lists.

    Enforces object-count and nesting-depth limits.
    """

    results = []
    stack = [(data, 0)]
    discovered_objects = 1

    while stack and len(results) < max_objects:

        current, depth = stack.pop()

        if depth > max_depth:
            continue

        if isinstance(current, dict):

            results.append(current)
            children = current.values()

        elif isinstance(current, list):

            children = current

        else:
            continue

        for value in children:

            if discovered_objects >= max_objects:
                break

            if isinstance(value, (dict, list)):
                stack.append((value, depth + 1))
                discovered_objects += 1

    return results


def is_assignment_object(obj):
    """
    Determine whether a JSON object looks like a Canvas assignment.

    This prevents parent objects such as assignment groups from
    being mistaken for assignments.
    """

    if not isinstance(obj, dict):
        return False

    # An assignment should have its own ID.
    if "id" not in obj:
        return False

    # Strong assignment indicators.
    assignment_indicators = {
        "course_id",
        "submission_types",
        "assignment_group_id",
        "grading_type",
        "points_possible",
        "workflow_state",
        "allowed_attempts",
        "due_at",
        "unlock_at",
        "lock_at"
    }

    matches = assignment_indicators.intersection(obj.keys())

    # Require multiple assignment-specific fields.
    return len(matches) >= 3

def extract_assignment(data):
    """
    Extract normalized information from a Canvas assignment object.

    The input must be the assignment itself, not the surrounding
    assignment group or another Canvas object.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "This JSON does not appear to be an assignment response. "
            "Expected a JSON object."
        )

    # Canvas may expose publication state through either
    # `published` or `workflow_state`.
    published = data.get("published")
    workflow_state = data.get("workflow_state")

    # If the boolean field is unavailable, use workflow_state
    # only when its meaning is explicit.
    if published is None:

        if workflow_state == "published":
            published = True

        elif workflow_state == "unpublished":
            published = False

    external_tool = data.get("external_tool_tag_attributes")

    assignment = {
        # Identity
        "assignment_id": data.get("id"),
        "assignment_group_id": data.get("assignment_group_id"),
        "course_id": data.get("course_id"),
        "name": data.get("name"),

        # Publication
        "published": published,
        "workflow_state": workflow_state,

        # Availability
        "due_at": data.get("due_at"),
        "unlock_at": data.get("unlock_at"),
        "lock_at": data.get("lock_at"),

        # Submission
        "submission_types": data.get("submission_types"),
        "submission_types_present": "submission_types" in data,
        "allowed_attempts": data.get("allowed_attempts"),

        # Grading
        "points_possible": data.get("points_possible"),
        "grading_type": data.get("grading_type"),

        # External tool / LTI
        "external_tool": external_tool,

        # Useful diagnostic state
        "has_submitted_submissions": data.get(
            "has_submitted_submissions"
        ),
        "graded_submissions_exist": data.get(
            "graded_submissions_exist"
        )
    }

    return assignment


def validate_assignment(assignment):
    """
    Identify missing assignment information.
    Missing information is reported for review,
    rather than preventing extraction.
    """

    errors = []

    if assignment.get("assignment_id") is None:
        errors.append("Assignment ID is missing.")

    if not assignment.get("name"):
        errors.append("Assignment name is missing.")

    if assignment.get("published") is None:
        errors.append("Publishing status is missing.")

    return errors


def process_assignment(file_path):
    """
    Load, extract, and validate a standalone assignment JSON file.
    """

    data = load_json(file_path)

    assignment = extract_assignment(data)

    errors = validate_assignment(assignment)

    return assignment, errors


def extract_modules(data):
    """
    Extract module information from a single module
    or a list of module objects.
    """

    if isinstance(data, dict):
        modules = [data]

    elif isinstance(data, list):
        modules = data

    else:
        return []

    extracted_modules = []

    for module in modules:

        if not isinstance(module, dict):
            continue

        extracted_modules.append({
            "module_id": module.get("id"),
            "name": module.get("name"),
            "published": module.get("published"),
            "position": module.get("position"),
            "unlock_at": module.get("unlock_at"),
            "require_sequential_progress": module.get(
                "require_sequential_progress"
            ),
            "requirement_type": module.get("requirement_type"),
            "items_count": module.get("items_count"),
            "items_url": module.get("items_url"),
            "items": module.get("items")
        })

    return extracted_modules


def extract_navigation(data):
    """
    Extract module navigation information from
    a parent object containing items and modules.
    """

    if not isinstance(data, dict):
        return {}

    navigation = {
        "items": [],
        "modules": []
    }

    items = data.get("items", [])

    if isinstance(items, list):

        for item in items:

            if not isinstance(item, dict):
                continue

            navigation["items"].append({
                "current": item.get("current"),
                "prev": item.get("prev"),
                "next": item.get("next")
            })

    modules = data.get("modules", [])

    if isinstance(modules, list):
        navigation["modules"] = extract_modules(modules)

    return navigation


def extract_configuration(data):
    """
    Extract Canvas integration configuration information.
    """

    if not isinstance(data, dict):
        return {}

    return {
        "lms_type": data.get("lmsType"),
        "flags": data.get("flags"),
        "academic_year_start": data.get("academicYearStart"),
        "configuration_id": data.get("id"),
        "microfrontends": data.get("microfrontends")
    }


def process_json(file_path):
    """
    Load JSON, recognize supported Canvas response types,
    and extract available information from nested data.
    """

    data = load_json(file_path)

    recognized_types = recognize_json(data)

    nested_objects = find_nested_objects(data)

    extracted_data = {}


    module_fields = {
        "require_sequential_progress",
        "requirement_type",
        "publish_final_grade",
        "prerequisite_module_ids",
        "items_count",
        "items_url"
    }

    # Assignment extraction
    if "assignment" in recognized_types:

        assignment_objects = [
            obj for obj in nested_objects
            if is_assignment_object(obj)
            ]

        if assignment_objects:
            extracted_data["assignment"] = extract_assignment(
                assignment_objects[0]
            )

    # Module extraction
    if "module" in recognized_types:

        module_objects = [
            obj for obj in nested_objects
            if (
                set(obj.keys()).intersection(module_fields)
                or {"name", "published", "items"}.issubset(obj.keys())
            )
        ]

        if module_objects:
            extracted_data["modules"] = extract_modules(
                module_objects
            )

    # Navigation extraction
    if "navigation" in recognized_types:

        navigation_objects = [
            obj for obj in nested_objects
            if {"items", "modules"}.issubset(obj.keys())
        ]

        if navigation_objects:
            extracted_data["navigation"] = extract_navigation(
                navigation_objects[0]
            )

    # Configuration extraction
    if "configuration" in recognized_types:

        configuration_objects = [
            obj for obj in nested_objects
            if (
                "lmsType" in obj
                or {"flags", "academicYearStart"}.issubset(obj.keys())
            )
        ]

        if configuration_objects:
            extracted_data["configuration"] = extract_configuration(
                configuration_objects[0]
            )

    return data, recognized_types, extracted_data
