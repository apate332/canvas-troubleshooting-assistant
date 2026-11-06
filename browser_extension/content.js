// ============================================================
// Canvas Troubleshooting Assistant
// content.js
// ============================================================


// ------------------------------------------------------------
// DETECT CURRENT CANVAS CONTEXT
// ------------------------------------------------------------

function detectCanvasContext() {
    const url =
        new URL(window.location.href);

    const pathParts =
        url.pathname
            .split("/")
            .filter(Boolean);

    const context = {
        isCanvasPage: false,
        pageType: null,
        courseId: null,
        activityId: null,
        moduleItemId: null,
        activityName: null,
        url: window.location.href
    };


    // --------------------------------------------------------
    // MODULE ITEM ID
    // Canvas may include this when an assignment is opened
    // through a module.
    // --------------------------------------------------------

    context.moduleItemId =
        url.searchParams.get(
            "module_item_id"
        );


    // --------------------------------------------------------
    // COURSE
    // --------------------------------------------------------

    const coursesIndex =
        pathParts.indexOf("courses");

    if (
        coursesIndex === -1 ||
        !pathParts[coursesIndex + 1]
    ) {
        return context;
    }

    context.isCanvasPage = true;

    context.courseId =
        pathParts[coursesIndex + 1];


    // --------------------------------------------------------
    // PAGE TYPE
    // --------------------------------------------------------

    const assignmentsIndex =
        pathParts.indexOf("assignments");

    const modulesIndex =
        pathParts.indexOf("modules");

    const quizzesIndex =
        pathParts.indexOf("quizzes");


    if (
        assignmentsIndex !== -1 &&
        pathParts[assignmentsIndex + 1]
    ) {
        context.pageType =
            "Assignment";

        context.activityId =
            pathParts[
                assignmentsIndex + 1
            ];

    } else if (
        quizzesIndex !== -1 &&
        pathParts[quizzesIndex + 1]
    ) {
        context.pageType =
            "Quiz";

        context.activityId =
            pathParts[
                quizzesIndex + 1
            ];

    } else if (
        modulesIndex !== -1
    ) {
        context.pageType =
            "Module";

        if (
            pathParts[
                modulesIndex + 1
            ]
        ) {
            context.activityId =
                pathParts[
                    modulesIndex + 1
                ];
        }

    } else {
        context.pageType =
            "Course";
    }


    // --------------------------------------------------------
    // ACTIVITY NAME
    // --------------------------------------------------------

    const heading =
        document.querySelector("h1") ||
        document.querySelector(
            '[data-testid="assignment-name"]'
        );

    if (heading) {
        context.activityName =
            heading.textContent.trim();

    } else {
        context.activityName =
            document.title
                .replace(
                    /\s*:\s*Canvas\s*$/i,
                    ""
                )
                .trim();
    }


    return context;
}


// ------------------------------------------------------------
// GET ASSIGNMENT CONFIGURATION
// ------------------------------------------------------------

async function getAssignmentData(
    context
) {
    if (
        context.pageType !==
            "Assignment" ||
        !context.courseId ||
        !context.activityId
    ) {
        throw new Error(
            "The current page is not a supported assignment page."
        );
    }


    const endpoint =
        `/api/v1/courses/${context.courseId}` +
        `/assignments/${context.activityId}`;


    const response =
        await fetch(
            endpoint,
            {
                method: "GET",

                credentials:
                    "same-origin",

                headers: {
                    "Accept":
                        "application/json"
                }
            }
        );


    if (!response.ok) {
        throw new Error(
            `Canvas returned ${response.status} while reading the assignment.`
        );
    }


    const assignment =
        await response.json();


    return {
        assignment_id:
            assignment.id,

        course_id:
            assignment.course_id,

        module_item_id:
            context.moduleItemId,

        name:
            assignment.name,

        published:
            assignment.published ??
            (
                assignment.workflow_state ===
                "published"
            ),

        workflow_state:
            assignment.workflow_state,

        due_at:
            assignment.due_at,

        unlock_at:
            assignment.unlock_at,

        lock_at:
            assignment.lock_at,

        submission_types:
            assignment.submission_types,

        points_possible:
            assignment.points_possible,

        grading_type:
            assignment.grading_type,

        allowed_attempts:
            assignment.allowed_attempts,

        assignment_group_id:
            assignment.assignment_group_id,

        external_tool:
            assignment
                .external_tool_tag_attributes
                ? {
                    url:
                        assignment
                            .external_tool_tag_attributes
                            .url,

                    resource_link_id:
                        assignment
                            .external_tool_tag_attributes
                            .resource_link_id,

                    content_type:
                        assignment
                            .external_tool_tag_attributes
                            .content_type
                }
                : null
    };
}


// ------------------------------------------------------------
// GET MODULE CONTEXT
// ------------------------------------------------------------

async function getModuleContext(
    context
) {
    /*
     * If the assignment was not opened through a module,
     * Canvas may not provide module_item_id in the URL.
     *
     * In that case we do NOT assume that there is no module.
     * We simply report that module context was not verified.
     */

    if (
        !context.courseId ||
        !context.moduleItemId
    ) {
        return null;
    }


    // --------------------------------------------------------
    // GET COURSE MODULES
    // --------------------------------------------------------

    const modulesEndpoint =
        `/api/v1/courses/${context.courseId}` +
        `/modules?per_page=100`;


    const modulesResponse =
        await fetch(
            modulesEndpoint,
            {
                method: "GET",

                credentials:
                    "same-origin",

                headers: {
                    "Accept":
                        "application/json"
                }
            }
        );


    if (!modulesResponse.ok) {
        console.warn(
            "Module context could not be collected:",
            modulesResponse.status
        );

        return null;
    }


    const modules =
        await modulesResponse.json();


    if (!Array.isArray(modules)) {
        return null;
    }


    // --------------------------------------------------------
    // FIND THE MODULE CONTAINING THE CURRENT MODULE ITEM
    // --------------------------------------------------------

    for (const module of modules) {

        if (!module || !module.id) {
            continue;
        }


        const itemsEndpoint =
            `/api/v1/courses/${context.courseId}` +
            `/modules/${module.id}/items` +
            `?per_page=100`;


        let itemsResponse;

        try {
            itemsResponse =
                await fetch(
                    itemsEndpoint,
                    {
                        method: "GET",

                        credentials:
                            "same-origin",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );

        } catch (error) {
            console.warn(
                "Could not read module items:",
                error
            );

            continue;
        }


        if (!itemsResponse.ok) {
            continue;
        }


        let items;

        try {
            items =
                await itemsResponse.json();

        } catch (error) {
            continue;
        }


        if (!Array.isArray(items)) {
            continue;
        }


        const currentItem =
            items.find(
                (item) =>
                    String(item.id) ===
                    String(
                        context.moduleItemId
                    )
            );


        if (!currentItem) {
            continue;
        }


        // ----------------------------------------------------
        // MODULE FOUND
        // ----------------------------------------------------

        return {
            module_id:
                module.id,

            module_name:
                module.name,

            module_published:
                module.published,

            module_item_id:
                currentItem.id,

            module_item_title:
                currentItem.title,

            module_item_type:
                currentItem.type,

            module_item_published:
                currentItem.published,

            content_id:
                currentItem.content_id,

            require_sequential_progress:
                module
                    .require_sequential_progress,

            requirement_type:
                module.requirement_type,

            module_unlock_at:
                module.unlock_at,

            prerequisite_module_ids:
                Array.isArray(
                    module
                        .prerequisite_module_ids
                )
                    ? module
                        .prerequisite_module_ids
                    : []
        };
    }


    // No matching module item was verified.
    return null;
}


// ------------------------------------------------------------
// MESSAGE HANDLER
// ------------------------------------------------------------

chrome.runtime.onMessage.addListener(
    (
        message,
        sender,
        sendResponse
    ) => {

        // ----------------------------------------------------
        // PING
        // Used by popup.js to determine whether this
        // content script is already available.
        // ----------------------------------------------------

        if (message.type === "PING") {
            sendResponse({
                ready: true
            });

            return false;
        }


// ----------------------------------------------------
// CANVAS CONTEXT
// ----------------------------------------------------

if (
    message.type ===
    "GET_CANVAS_CONTEXT"
) {
    sendResponse(
        detectCanvasContext()
    );

    return false;
}


// ----------------------------------------------------
// ASSIGNMENT + MODULE CONFIGURATION
// ----------------------------------------------------

        if (
            message.type ===
            "GET_ASSIGNMENT_DATA"
        ) {
            const context =
                detectCanvasContext();


            Promise.all([
                getAssignmentData(
                    context
                ),

                getModuleContext(
                    context
                )
            ])
                .then(
                    ([
                        assignment,
                        moduleContext
                    ]) => {

                        assignment
                            .module_context =
                            moduleContext;


                        sendResponse({
                            success: true,
                            assignment:
                                assignment
                        });
                    }
                )
                .catch(
                    (error) => {

                        console.error(
                            "Canvas configuration collection failed:",
                            error
                        );


                        sendResponse({
                            success: false,
                            error:
                                error.message
                        });
                    }
                );


            /*
             * Keep the Chrome message channel open
             * while the asynchronous Canvas requests
             * complete.
             */
            return true;
        }


        return false;
    }
);