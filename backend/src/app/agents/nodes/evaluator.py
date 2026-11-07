def evaluator_node(state):

    plan = state.get("plan", {})

    issues = []

    if (
        plan.get("needs_payment_metrics")
        and not state.get("metrics")
    ):
        issues.append("Financial metrics are missing.")

    if (
        plan.get("needs_document_search")
        and not state.get("research_completed")
    ):
        issues.append("Research has not completed.")

    if not state.get("analyst_result"):
        issues.append("Analyst findings are missing.")

    status = bool(not issues)

    return {
        "validation_issues": issues,
        "evaluation_passed": status,
    }