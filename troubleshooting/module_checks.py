
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
