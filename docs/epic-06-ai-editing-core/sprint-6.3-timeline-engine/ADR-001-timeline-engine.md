# ADR-001

Title

Timeline JSON as the Single Source of Truth

Status

Accepted

---

# Context

Traditional video editors manipulate media directly.

AI Clip Agent requires deterministic, reproducible editing.

A structured Timeline enables reproducible rendering, validation, testing, and future integrations.

---

# Decision

All editing decisions shall be represented as Timeline Events.

The Renderer shall consume Timeline JSON exclusively.

No rendering logic shall contain AI decision-making.

---

# Consequences

Positive

- Deterministic rendering.
- Easier debugging.
- Renderer independence.
- Multiple render backends can be supported.

Trade-offs

- Initial design complexity.
- Timeline schema must remain stable.
- Requires validation layer before rendering.

---

# Long-term Vision

Timeline JSON becomes the universal editing language of AI Clip Agent.

Any AI model, editor, or integration capable of producing a valid Timeline JSON can use the rendering pipeline without modification.