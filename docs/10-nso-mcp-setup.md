---
title: "Lab 10: NSO MCP — Setup and First Client"
chapter: 10

nso_version: "6.7"
ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "80 min"
prerequisites:
  - "Labs 1–9 completed (Day 1 + Day 2 morning)."
  - "Access to a dCloud session for the NSO 6.7 MCP scenario (Ubuntu 24.04 Desktop reachable at 198.18.134.27)."
learning_objectives:
  - "Explain what the Model Context Protocol (MCP) provides: resources, tools, and prompts."
  - "Install NSO 6.7 LTS in the dCloud Ubuntu host and confirm both XRd devices are reachable."
  - "Install the NSO MCP package, enable the MCP server, and verify with the bundled test script."
  - "Launch the sample web MCP client and interact with NSO using natural language."
  - "Switch the MCP policy from restricted to permit and observe the expanded tool set."
idempotent: false
classification: "Cisco Confidential"
---

# Lab 10: NSO MCP — Setup and First Client

!!! info "Day 2 — Afternoon session"
<!-- lint-allow-hardcoded-version -->
    Day 2 morning covered **RBAC** and the full lifecycle of NSO administration (Labs 5–9). This afternoon session pivots to **NSO 6.7**, where the headline feature is the **Model Context Protocol (MCP) server**. You will set up a fresh NSO 6.7 instance, expose it through MCP, and drive NSO with a natural-language client — all in the dCloud all-in-one scenario.

!!! warning "NSO version difference"
<!-- lint-allow-hardcoded-version -->
    Labs 1–9 use NSO 6.5. This lab and Lab 11 require **NSO 6.7 LTS**, which is the version bundled in the dCloud "NSO 6.7 MCP" scenario. Commands and paths in this chapter reference `NSO-6.7-LTS-free/` explicitly because MCP is only available from 6.7 onward.

## Learning Objectives

By the end of this lab you will be able to:

- Describe the three building blocks MCP exposes: **resources**, **tools**, and **prompts**.
<!-- lint-allow-hardcoded-version -->
- Install NSO 6.7 on the dCloud Ubuntu host via the provided Ansible playbook and confirm both XRd routers are in sync.
- Install the **NSO MCP package**, enable the MCP server, and verify it with the bundled `test-mcp.sh` script (all 5 tests passing).
- Launch the sample **web MCP client** (`backend.py` + Streamlit `frontend.py`) and interact with NSO using natural language through a browser.
- Switch the MCP policy from the default `restricted` (~11 tools) to `permit` (100+ tools) and observe the larger surface area.

## Time Budget

<!-- lint-allow-hardcoded-version -->
{{ time_budget(total=80, segments=[[8,"What is MCP?"],[20,"Setup NSO 6.7"],[20,"Install MCP package"],[18,"Run web client"],[14,"Change policy"]]) }}

## Prerequisites

- [ ] [Lab 9: RBAC Access Control](09-rbac-access-control.md) completed — the Day 2 morning track is done.
<!-- lint-allow-hardcoded-version -->
- [ ] Your dCloud session for **NSO 6.7 MCP — Demo** is **Active** (all stages of the Launch Progress bar are green; this can take up to ~10 minutes).
- [ ] You can open the **VM Console** of **Ubuntu 24.04 Desktop**.

## What is MCP?

<!-- lint-allow-hardcoded-version -->
The **Model Context Protocol (MCP)** acts as a universal translator between data sources and AI applications. **NSO 6.7** can act as an **MCP server** and exposes three primitives:

| MCP primitive | What NSO provides |
|---------------|-------------------|
| **Resources** — schema and data | `global-settings`, `zombies`, device settings and configurations |
| **Tools** — executable functions the LLM can call | Configurable via `mcp-policies` (the policy decides which tools are exposed) |
| **Prompts** — pre-defined templates | Seven prompts shipped with the NSO MCP server |

In this lab, a custom **MCP client** (used later in the procedure) connects to NSO and leverages **Cisco AI** to provide an AI interface through a web browser.

## Procedure

!!! warning "Rollback"
    <!-- lint-allow-hardcoded-version -->
    This lab is **not idempotent** — it installs NSO 6.7 fresh and enables the MCP server with a permissive policy. To roll back the MCP changes without reinstalling NSO, in the NSO CLI:

    ```text
    admin@ncs# config t
    admin@ncs(config)# no mcp-server enabled
    admin@ncs(config)# mcp-server policies default-action restricted
    admin@ncs(config)# commit
    ```

    To fully undo the install, the simplest path in the dCloud scenario is to **end the dCloud session** and restart it — the Ansible playbook will reprovision the host.

### Step 1: Validate the running NSO 6.5 instance and shut it down

Before moving to the new dCloud scenario you must cleanly stop the NSO 6.5 instance that has been running throughout Labs 1–9. Work on the **xrd-host** terminal you have been using all day.

Source the NSO 6.5 environment and confirm the version:

```bash
source ~/NSO-INSTALL/ncsrc
ncs --version
```

<!-- lint-allow-hardcoded-version -->
The output must show **6.5** — this confirms the correct environment is sourced.

```text
6.5
```

Stop the NSO 6.5 daemon:

```bash
ncs --stop 2>/dev/null || true
```

Verify the daemon is no longer listening:

```bash
ncs --status
```

Expected output:

```text
connection refused (status)
```

`connection refused` means NSO 6.5 has stopped cleanly. You can now proceed to the new dCloud scenario that bundles **NSO 6.7**.

---

### Step 2: Open a terminal on the Ubuntu host

Once the dCloud scenario is active, open the **VM Console** of **Ubuntu 24.04 Desktop**.

![dCloud VM Console launcher for Ubuntu 24.04 Desktop](assets/images/lab10/dcloud-vm-console-ubuntu.png)


On Ubuntu, open **Terminal**.

<!-- lint-allow-hardcoded-version -->
### Step 3: Install NSO 6.7 with the provided Ansible playbook

<!-- lint-skip: no-output -->
```bash
cd ~/NSO-6.7-LTS-free
ansible-playbook nso.yml
```

Wait a few minutes for the playbook to complete — NSO will be installed automatically.

Once it finishes, source the environment and open the NSO CLI:

<!-- lint-skip: no-output -->
```bash
cd
source NSO-6.7/ncsrc
ncs_cli -Cu admin
```

### Step 4: Confirm the XRd routers are reachable

Inside the NSO CLI, sync both XRd devices and verify they are present:

```text
admin@ncs# devices sync-from
admin@ncs# show devices device
```

{{ expected_output(landmark="two XRd devices listed and sync-from result: true") }}

![NSO CLI showing devices sync-from with two XRd routers in sync](assets/images/lab10/nso-cli-sync-from-xrd.png)

If either device fails to sync, stop here and resolve before continuing — MCP needs a working device tree to expose meaningful tools.

### Step 5: Install the NSO MCP package

The MCP package is included in the NSO installer bundle. From the **Linux terminal** (not the NSO CLI), copy it into the packages directory:

<!-- lint-skip: no-output -->
```bash
cd
cp NSO-6.7-LTS-free/work/ncs-6.7-cisco-nso-adaptive-mcp-server-1.0.0.tar.gz ncs-run/packages
```

Then in the **NSO CLI**, reload packages and enable MCP:

```text
admin@ncs# packages reload
admin@ncs# config t
admin@ncs(config)# mcp-server enabled
admin@ncs(config)# commit
admin@ncs(config)# end
```

### Step 6: Verify the MCP server with the bundled test script

The MCP package contains a `test-mcp.sh` test script. Confirm MCP is up and running:

<!-- lint-skip: no-output -->
```bash
cd
tar zxvf NSO-6.7-LTS-free/work/ncs-6.7-cisco-nso-adaptive-mcp-server-1.0.0.tar.gz
cd cisco-nso-adaptive-mcp-server
./test-mcp.sh
```

If any test fails, go back to the NSO CLI, run `packages reload` again, and re-run `./test-mcp.sh`. Continue only when **all 5 tests pass**.

![test-mcp.sh output showing all 5 tests passed](assets/images/lab10/test-mcp-all-tests-passed.png)

NSO MCP is now ready.

### Step 7: Start the web MCP client (backend + frontend)

The scenario includes a sample web MCP client. It runs as two programs in two terminal tabs.

**Terminal tab 1 — backend:**

<!-- lint-skip: no-output -->
```bash
cd
cd NSO-6.7-LTS-free/web-ui
source venv/bin/activate
python3 backend.py
```

**Terminal tab 2 — frontend** (open a new tab, then):

<!-- lint-skip: no-output -->
```bash
cd NSO-6.7-LTS-free/web-ui
source venv/bin/activate
streamlit run frontend.py
```

Firefox should open automatically. If not, launch Firefox manually and browse to <http://localhost:8501/>.

Confirm the **NSO MCP tools** appear in the left-hand menu of the web UI:

![Streamlit web MCP client with NSO MCP tools listed on the left menu](assets/images/lab10/mcp-web-client-tools-menu.png)

### Step 8: Drive NSO with natural language

In the chat box, ask NSO about its devices in plain English (e.g. *"List the devices managed by NSO."*).

![Web MCP client answering a natural-language question about NSO devices](assets/images/lab10/mcp-web-client-natural-language.png)

### Step 9: Change the MCP policy from `restricted` to `permit`

By default, for security reasons, the active MCP policy is **`restricted`** — it exposes only **11 tools**. Switch the default action to **`permit`** so more tools become available.

In the NSO CLI:

```text
$ ncs_cli -Cu admin
admin@ncs# config t
admin@ncs(config)# mcp-server policies default-action permit
admin@ncs(config)# commit
admin@ncs(config)# end
```

Back in the web MCP client, press **Refresh tools** in the left menu. You should now see **more than 100 tools**:

![MCP web client left menu showing 100+ tools after policy change to permit](assets/images/lab10/mcp-policy-permit-100-tools.png)

You can now run richer queries — for example, ask the client to show **`live-status`** of a device:

![MCP web client returning live-status output for an XRd device](assets/images/lab10/mcp-live-status-result.png)

!!! warning "Production policy"
    `permit` exposes a very large surface area to whichever LLM is on the other end of the MCP connection. Use `restricted` (or a hand-curated policy) for anything other than demo / lab scenarios.

## Verification

You should now have:

<!-- lint-allow-hardcoded-version -->
- [ ] NSO 6.7 LTS installed on the Ubuntu host, with both XRd routers in **sync-from: true**.
- [ ] NSO MCP package loaded, MCP server **enabled** in the running config.
- [ ] `./test-mcp.sh` reporting **5/5 tests passed**.
- [ ] The web MCP client running on <http://localhost:8501/> with the NSO tool menu populated.
- [ ] MCP policy switched to **`permit`** — the tool count in the left menu jumps from ~11 to **100+**.

## Troubleshooting

- **`test-mcp.sh` fails** — run `packages reload` in the NSO CLI, wait for it to finish, and re-run the test script.
- **No tools visible in the web client** — the policy may still be `restricted` and connection-scoped. Confirm `mcp-server policies default-action permit` was committed, then press **Refresh tools**.
- **Streamlit page won't load** — verify both `backend.py` and `streamlit run frontend.py` are running in their own terminal tabs with the venv activated.

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "`./test-mcp.sh` reports fewer than 5 passing tests after `packages reload`.",
  "MCP package partially loaded — `mcp-server enabled` was committed before `packages reload` finished, or the tarball was not copied into `ncs-run/packages` before the reload.",
  "Re-run `packages reload` in the NSO CLI and wait for it to return cleanly, then run `./test-mcp.sh` again. If the tarball is missing under `ncs-run/packages`, repeat Step 4 (`cp …adaptive-mcp-server…tar.gz ncs-run/packages`)."
) }}

{{ common_error(
  "Web client shows only ~11 tools even after pressing **Refresh tools**.",
  "MCP policy is still the default `restricted`, or the commit of `default-action permit` was rolled back.",
  "In the NSO CLI, run `show running-config mcp-server policies default-action` — if it does not say `permit`, repeat Step 8 and commit. Then press **Refresh tools** in the web client."
) }}

{{ common_error(
  "Firefox cannot reach <http://localhost:8501/>.",
  "The Streamlit frontend (`streamlit run frontend.py`) is not running, or its terminal has lost the activated venv.",
  "Open the frontend terminal tab, confirm the prompt has `(venv)`, and re-run `streamlit run frontend.py`. The backend (`python3 backend.py`) must also be running in its own tab."
) }}

{{ common_errors_end() }}

## What's Next

Lab 10 left NSO MCP exposed with the broad **`permit`** policy. In [Lab 11: NSO MCP — Service Models and BGP](11-nso-mcp-services-bgp.md) you will **load an additional service package** (`bgpmgr`), watch its tools appear in the MCP client, and use natural language to **configure BGP** between **xr-1** and **xr-2** — then inspect the available tools and prompts from a second MCP client (`ollmcp`).
