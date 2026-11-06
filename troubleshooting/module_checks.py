
def check_module_published(module):

    findings = []

    if not isinstance(module, dict):
        return findings

    if module.get("published") is False:

        module_name = module.get("name") or "Unknown"

        findings.append({
            "issue": f"Module '{module_name}' is unpublished",
            "severity": "Warning",
            "recommendation": (
                "Review whether this module should be published."
            )
        })

    return findings


def check_module_items(module):

    findings = []

    if not isinstance(module, dict):
        return findings

    module_name = module.get("name") or "Unknown"

    # Only inspect items when Canvas actually provides
    # the items field as a list.
    if "items" not in module:
        return findings

    items = module.get("items")

    # Missing or null item information is not proof
    # that the module contains no items.
    if not isinstance(items, list):
        return findings

    # An explicitly provided empty list means that
    # Canvas returned no items in this response.
    if len(items) == 0:

        findings.append({
            "issue": f"Module '{module_name}' has no items",
            "severity": "Review",
            "recommendation": (
                "Verify whether this module should contain assignments, "
                "pages, quizzes, or other course content."
            )
        })

        return findings

    for item in items:

        if not isinstance(item, dict):
            continue

        if item.get("published") is False:

            item_title = item.get("title") or "Unknown"

            findings.append({
                "issue": (
                    f"Module item '{item_title}' is unpublished"
                ),
                "severity": "Warning",
                "recommendation": (
                    "Review whether this module item should be published."
                )
            })

    return findings


def check_assignment_module_context(assignment):
    """
    Check the module containing the current assignment.

    Module context is only evaluated when it was
    successfully collected by the browser extension.
    """

    findings = []

    if not isinstance(assignment, dict):
        return findings

    module_context = assignment.get(
        "module_context"
    )

    # Module context was not available.
    # This does NOT mean the assignment is not in a module.
    if not isinstance(module_context, dict):
        return findings

    module_name = module_context.get(
        "module_name",
        "Containing module"
    )

    module_published = module_context.get(
        "module_published"
    )

    module_item_published = module_context.get(
        "module_item_published"
    )

    # --------------------------------------------------
    # MODULE UNPUBLISHED
    # --------------------------------------------------

    if module_published is False:
        findings.append({
            "issue": "Containing module is unpublished",
            "severity": "Warning",
            "recommendation": (
                f'The assignment is inside "{module_name}", '
                "which is currently unpublished. "
                "Publish the module if students are expected "
                "to access this activity through Modules."
            )
        })

    # --------------------------------------------------
    # MODULE ITEM UNPUBLISHED
    # --------------------------------------------------

    if module_item_published is False:
        findings.append({
            "issue": "Module item is unpublished",
            "severity": "Warning",
            "recommendation": (
                "The assignment's module item is currently "
                "unpublished. Publish the module item if "
                "students should access it through the module."
            )
        })

    return findings
