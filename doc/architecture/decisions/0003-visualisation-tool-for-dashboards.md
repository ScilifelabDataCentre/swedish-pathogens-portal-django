# 3. Visualisation tool for Dashboards

**Date:** 2025-11-13

## Status

Accepted

## Context

In Swedish Pathogens Portal, we develop and manage multiple dashboards. Each dashboard presents unique (and sometime multiple) plot. To support data visualization needs, we evaluated two main options for generating and displaying plots:

- Plotly _(integrated directly within the Django app)_

- Apache Superset _(as an external visualization service)_

The main goal was to find a solution that provides flexibility, ease of integration, and sufficient control over how plots are generated and displayed.

## Decision

We decided to use **Plotly** as the primary plotting library for generating visualizations for our dashboards.

**Rationale:**

- **Flexibility and Control:** Plotly allows full programmatic control over plot generation directly in Python, which fits well with our existing Django backend and development workflow.

- **Simplicity of Integration:** Since our current requirements are modest, embedding Plotly charts directly within Django templates avoids the overhead of managing a separate visualization service.

**Considered Alternatives:**

- **Apache Superset:**

    - _Pros:_ Robust visualization platform, role-based access control, built-in dashboarding features.

    - _Cons:_ Adds operational overhead (requires a separate service), less flexible for embedding custom plots in Django templates, and our current visualization needs do not justify the added complexity.

## Consequences

- Plot generation logic remains tightly coupled to the Django codebase, which is acceptable for the current project scale.

- If dashboards evolve into more complex or user-driven analytic interfaces, we may need to re-evaluate Superset or a similar dedicated BI solution in the future
