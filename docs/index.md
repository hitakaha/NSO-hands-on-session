---
hide:
  - navigation
classification: "Cisco Confidential"
---

# ~6 hours, 11 labs — build an NSO service that survives real drift, then drive NSO with natural language

{{ home_subtitle(text="For network engineers and automation leads working through a guided Cisco NSO hands-on lab with XRd peers — now extended with an NSO 6.7 MCP afternoon track.") }}

{{ home_meta() }}

## Reference topology

{{ topology(diagram_id="lab-home-topology", chapter="index", caption="Lab sandbox — workstation, NSO, and XRd peers") }}

## Lab journey

{{ journey_table() }}

!!! info "Two-day flow"
    Labs **1–11** run on the standard NSO **{{ nso_version }}** sandbox (Day 1 + Day 2 afternoon). Labs **10–11** are a **Day 2 afternoon** continuation using the dCloud **"NSO 6.7 MCP"** scenario — a NSO release, and the new **Model Context Protocol** server. Each chapter declares its own NSO version in front-matter.

!!! info "Before you begin"
    Provision your sandbox and open a console to the **linux-host** workstation. Commands assume that environment unless noted.
