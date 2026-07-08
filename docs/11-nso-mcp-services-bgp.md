---
title: "Lab 11: NSO MCP — Service Models and BGP"
chapter: 11

nso_version: "6.7"
ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "70 min"
prerequisites:
  - "Lab 10: NSO MCP — Setup and First Client completed."
  - "NSO MCP server running on the dCloud Ubuntu host with policy default-action set to permit."
  - "The web MCP client (Streamlit) reachable at http://localhost:8501/."
learning_objectives:
  - "Clone, compile, and load a custom service package (bgpmgr) into NSO."
  - "Observe a service package's tools appear automatically in the MCP client after a packages reload + Refresh Tools."
  - "Use natural language through the MCP client to discover required service parameters and configure BGP between xr-1 and xr-2."
  - "Verify BGP neighbor state via MCP without dropping back to per-device CLI."
  - "Use a second MCP client (ollmcp) to inspect available tools and prompts."
idempotent: false
classification: "Cisco Confidential"
---

# Lab 11: NSO MCP — Service Models and BGP

!!! info "Continuing from Lab 10"
    Lab 10 ended with NSO MCP exposed via the **permit** policy and the **web MCP client** running on <http://localhost:8501/>. In this lab you will plug a real **service package** (`bgpmgr`) into the same MCP client and configure **BGP** between **xr-1** and **xr-2** using natural language — then look under the hood with a second MCP client.

## Learning Objectives

By the end of this lab you will be able to:

- Clone and compile a custom NSO service package (`dcloud-bgpmgr`) and load it via `packages reload`.
- Confirm that the package's tools appear in the MCP web client after pressing **Refresh Tools**.
- Use the MCP client to ask **what parameters** the BGP service requires, and to **apply** the configuration.
- Verify BGP neighbor state through MCP (no direct `show bgp` on the device CLI required).
- Launch the **`ollmcp`** CPU-only MCP client and list NSO **tools** and **prompts** via `/t` and `/prompts`.

## Time Budget

{{ time_budget(total=70, segments=[[18,"Load bgpmgr package"],[12,"Inspect MCP tools"],[28,"Configure BGP via MCP"],[12,"Analyze with ollmcp"]]) }}

## Prerequisites

- [ ] [Lab 10: NSO MCP — Setup and First Client](10-nso-mcp-setup.md) completed.
<!-- lint-allow-hardcoded-version -->
- [ ] NSO 6.7 LTS is running, MCP server is **enabled** and **policy default-action is `permit`** (100+ tools visible in the web client).
- [ ] The web MCP client is reachable at <http://localhost:8501/>.
- [ ] Both **xr-1** and **xr-2** are in `sync-from: true` state.

## Procedure

!!! warning "Rollback"
    This lab is **not idempotent** — it loads a service package and writes BGP configuration to **xr-1** and **xr-2** via that package. To roll back, in the NSO CLI:

    ```text
    admin@ncs# config t
    admin@ncs(config)# devices device xr-1 config no router bgp
    admin@ncs(config)# devices device xr-2 config no router bgp
    admin@ncs(config)# commit
    ```

    To also remove the `bgpmgr` package, delete it from `~/ncs-run/packages/dcloud-bgpmgr` and run `packages reload` in the NSO CLI.

### Step 1: Clone and compile the `bgpmgr` service package

Loading a service package adds extra tools to NSO MCP automatically. Clone the demo package into the NSO packages directory:

<!-- lint-skip: no-output -->
```bash
cd
cd ncs-run/packages
git clone https://github.com/hitakaha/dcloud-bgpmgr.git
```

Compile the package:

<!-- lint-skip: no-output -->
```bash
cd dcloud-bgpmgr/src
make clean
make
```

### Step 2: Load the package into NSO

In the NSO CLI:

```text
$ ncs_cli -Cu admin
admin@ncs# packages reload
```

Wait for the reload to complete.

### Step 3: Confirm `bgpmgr` tools appear in the MCP web client

Go back to the **web-ui** (<http://localhost:8501/>) and press **Refresh Tools** on the left menu. You should now see **`bgpmgr`** tools listed alongside the core NSO tools.

![Web MCP client left menu showing bgpmgr service tools loaded](assets/images/lab11/mcp-bgpmgr-tools-loaded.png)

### Step 4: Clear any existing BGP configuration on `xr-1` and `xr-2`

Both XRd routers currently carry BGP configuration from earlier labs. Remove it through NSO so we have a clean slate to configure via MCP:

```text
$ ncs_cli -Cu admin
admin@ncs# config t
admin@ncs(config)# devices device xr-1 config
admin@ncs(config-config)# no router bgp
admin@ncs(config-config)# top
admin@ncs(config)# devices device xr-2 config
admin@ncs(config-config)# no router bgp
admin@ncs(config-config)# commit
```

### Step 5: Confirm there are no BGP neighbors — via MCP

In the web MCP client, ask the assistant to verify there are no BGP neighbors:

> *"List BGP neighbors on xr-1 and xr-2."*

![MCP web client confirming there are no BGP neighbors on xr-1 or xr-2](assets/images/lab11/mcp-no-bgp-neighbors.png)

### Step 6: Ask the assistant which parameters `bgpmgr` needs

Use the MCP client to discover the package surface without reading the YANG model directly:

> *"What parameters do I need to configure BGP through the bgpmgr package?"*

![MCP web client explaining the required parameters for the bgpmgr service](assets/images/lab11/mcp-bgpmgr-required-parameters.png)

### Step 7: Configure BGP between `xr-1` and `xr-2` through the assistant

Now ask the assistant to configure BGP using the parameters it just listed:

> *"Configure BGP between xr-1 and xr-2 using bgpmgr."*

The assistant will translate your request into the appropriate `bgpmgr` service invocation and commit it through NSO.

![MCP web client driving the bgpmgr service to configure BGP between xr-1 and xr-2](assets/images/lab11/mcp-configure-bgp.png)

### Step 8: Verify BGP neighbors are up — via MCP

Ask the assistant again, the same way you would ask a colleague:

> *"Are the BGP neighbors up between xr-1 and xr-2?"*

![MCP web client showing BGP neighbors in Established state between xr-1 and xr-2](assets/images/lab11/mcp-bgp-neighbors-up.png)

### Step 9: Inspect MCP tools and prompts with `ollmcp`

The scenario ships a second MCP client (`ollmcp`) intended for Ollama. We will use it purely for **analysis** — listing what NSO MCP exposes.

Open a new terminal tab and run:

<!-- lint-skip: no-output -->
```bash
cd
cd NSO-6.7-LTS-free/ollmcp
source venv/bin/activate
ollmcp -j ollama-mcp-config.json
```

At the `ollmcp` prompt, type **`/t`** to list all NSO tools currently exposed by MCP:

![ollmcp tool listing for NSO MCP](assets/images/lab11/ollmcp-tools-listing.png)

Type **`/prompts`** to list all available MCP prompts:

![ollmcp prompts listing for NSO MCP](assets/images/lab11/ollmcp-prompts-listing.png)

For more information about this client, see <https://github.com/jonigl/mcp-client-for-ollama>.

!!! note "ollmcp performance"
    The Ollama-based MCP client in this scenario runs **CPU-only (no GPU)** and is consequently very slow. Treat it as an analysis / introspection tool, not an interactive assistant.

## Verification

You should now have:

- [ ] The **`bgpmgr`** package compiled and loaded — its tools appear in the MCP web client after **Refresh Tools**.
- [ ] BGP configuration on **xr-1** / **xr-2** authored end-to-end **through MCP** (no manual `router bgp` block typed by hand).
- [ ] BGP neighbors between **xr-1** and **xr-2** reported as **up / Established** by the MCP assistant.
- [ ] **`ollmcp`** running and able to list NSO tools (`/t`) and prompts (`/prompts`).

## Troubleshooting

- **`bgpmgr` tools don't appear after Refresh Tools** — confirm `packages reload` finished cleanly in the NSO CLI (`show packages package bgpmgr oper-status`). Then press **Refresh Tools** again.
<!-- lint-allow-hardcoded-version -->
- **`make` fails compiling the package** — verify you are inside `~/ncs-run/packages/dcloud-bgpmgr/src/` and that `NSO-6.7/ncsrc` has been sourced in the shell.
- **MCP cannot reach the devices** — re-check `devices sync-from` in NSO CLI and that the device authgroups still resolve.
- **The assistant refuses or returns an empty plan** — your MCP policy may have been switched back to `restricted`. Re-verify `mcp-server policies default-action permit` is committed.

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "`bgpmgr` tools never appear in the MCP web client.",
  "`packages reload` failed (compile error in `dcloud-bgpmgr/src/`) or finished with the package in error state, so MCP cannot expose its tools.",
  "Run `show packages package dcloud-bgpmgr oper-status` in the NSO CLI. If `oper-status` is anything other than `up`, rebuild: `cd ~/ncs-run/packages/dcloud-bgpmgr/src && make clean && make`, then re-run `packages reload` and press **Refresh Tools** in the web client."
) }}

{{ common_error(
  "Assistant says BGP is configured, but neighbors do not come up.",
  "AS numbers, neighbor addresses, or update-source were inferred incorrectly by the LLM (e.g., neighbor address pointed at a loopback that is not advertised yet).",
  "Ask the assistant to *'show the running BGP configuration on xr-1 and xr-2'* and reconcile against the topology table in Lab 10. Re-invoke the `bgpmgr` service with corrected parameters and commit."
) }}

{{ common_error(
  "Assistant refuses to act or returns an empty plan in this lab.",
  "MCP policy was reverted to `restricted` between Lab 10 and Lab 11, so the service-write tools are no longer exposed.",
  "In the NSO CLI: `show running-config mcp-server policies default-action` — if it does not say `permit`, repeat Step 8 of Lab 10."
) }}

{{ common_errors_end() }}

## What's Next

<!-- lint-allow-hardcoded-version -->
Labs 10 and 11 introduced **NSO 6.7 MCP** as a way to drive NSO with natural language and to plug custom service packages into the same interface. From here, useful next steps outside this workbook include:

- Designing a **custom `mcp-server policies`** that exposes only the tools your operators should actually use (vs. the broad `permit` default).
- Building your own service package and watching its tools appear automatically in the MCP client — the workflow is the same as `bgpmgr` in this lab.
- Wiring MCP into a production-grade client (the **`web-ui`** and **`ollmcp`** clients in this scenario are demonstrations — real deployments will use a different client/LLM combination).
