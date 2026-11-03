
def recognize_json(data, max_objects=10000, max_depth=50):
    """
    Identify supported Canvas response types in JSON data.

    Searches nested dictionaries and lists while enforcing
    object-count and nesting-depth limits.
    """

    recognized_types = []

    assignment_fields = {
        "due_at",
        "submission_types",
        "only_visible_to_overrides",
        "visible_to_everyone",
        "group_category_id",
        "graded",
        "overrides"
    }

    module_fields = {
        "require_sequential_progress",
        "requirement_type",
        "publish_final_grade",
        "prerequisite_module_ids",
        "items_count",
        "items_url"
    }

    def add_type(response_type):
        if response_type not in recognized_types:
            recognized_types.append(response_type)

    # Each stack entry contains the object and its nesting depth.
    stack = [(data, 0)]
    discovered_objects = 1
    inspected_objects = 0

    while stack and inspected_objects < max_objects:

        current, depth = stack.pop()

        if depth > max_depth:
            continue

        if not isinstance(current, (dict, list)):
            continue

        inspected_objects += 1

        if isinstance(current, dict):

            keys = set(current.keys())

            # Assignment detection (ID is not required).
            if keys.intersection(assignment_fields):
                add_type("assignment")

            # Module detection (ID is not required).
            if (
                keys.intersection(module_fields)
                or {"name", "published", "items"}.issubset(keys)
            ):
                add_type("module")

            # Navigation response detection.
            if (
                {"current", "prev", "next"}.issubset(keys)
                or {"items", "modules"}.issubset(keys)
            ):
                add_type("navigation")

            # Configuration response detection.
            if (
                "lmsType" in keys
                or {"flags", "academicYearStart"}.issubset(keys)
            ):
                add_type("configuration")

            children = current.values()

        else:
            children = current

        # Add nested objects without exceeding the object limit.
        for value in children:

            if discovered_objects >= max_objects:
                break

            if isinstance(value, (dict, list)):
                stack.append((value, depth + 1))
                discovered_objects += 1

    if not recognized_types:
        return ["unknown"]

    return recognized_types
