---
title: "Lab 5: Rollbacks"
chapter: 5

ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "20 min"
prerequisites:
  - "Lab 4: Configure Devices completed — you committed a change on xr-1 (for example IPv4 10.1.1.30 on GigabitEthernet0/0/0/0)."
learning_objectives:
  - "Locate rollback metadata in Commit Manager and load a rollback file."
  - "Commit a loaded rollback as a new candidate and push it through Commit Manager."
  - "Verify on the device that configuration matches the rollback (for example IPv4 10.1.1.3)."
idempotent: true
classification: "Cisco Confidential"
---

# Lab 5: Rollbacks

## Learning Objectives

By the end of this lab you will be able to:

- Locate rollback metadata in **Commit Manager** and load a rollback file.
- Commit a loaded rollback as a new candidate and complete the workflow in Commit Manager.
- Verify on the device CLI that configuration matches the rolled-back state.

## Time Budget

{{ time_budget(total=20, segments=[[8,"Load rollback"],[12,"Verify on device"]]) }}

## Prerequisites

- [ ] [Lab 4: Configure Devices](04-configure-devices.md) completed — at least one successful **commit** exists so NSO generated rollback files.
- [ ] You can open the NSO Web UI as **admin** and SSH from **linux-host** to **xr-1** (use the management IP from your lab sheet; examples use **172.30.0.2**).

## Procedure

NSO creates a **rollback file** for every commit so you can revert configuration changes safely.

### Step 1: Open Commit Manager

1. Go to **Commit Manager**.
2. Click **Load/Save**.
3. Select the rollback file that corresponds to the state **before** the Lab 4 address change (metadata shows **User**, **Northbound interface**, timestamp — pick the rollback that restores **10.1.1.3** on the interface).

![Commit Manager Load/Save — Rollbacks tab showing recent commits by admin via webui](assets/images/lab05/webui-rollback-load-save.png)

### Step 2: Load the rollback

1. Click **Load** — the revert appears as a **candidate** configuration.
2. Review the diff: the rollback reverses Lab 4's change (**10.1.1.30** removed → **10.1.1.3** restored).

![Rollback diff — ip 10.1.1.30 (red, removed) → ip 10.1.1.3 (green, restored)](assets/images/lab05/webui-rollback-diff-loaded.png)

3. Click **Commit** to apply.

![Commit confirmation for the rollback — click Yes, commit](assets/images/lab05/webui-rollback-commit-result.png)

### Step 3: Verify on the device

SSH to **xr-1** and confirm the IPv4 address on the data interface is restored to **10.1.1.3**.

<!-- lint-skip: no-output -->

```bash
ssh admin@172.30.0.2
(admin@172.30.0.2) Password: (password = cisco123)
```

*(Replace with your lab management address.)*

At the XR prompt:

```cli
show run interface gigabitEthernet 0/0/0/0
```

{{ expected_output(landmark="10.1.1.3") }}

*Expected output:*

```text
interface GigabitEthernet0/0/0/0
 ipv4 address 10.1.1.3 255.255.255.0
!
```

*(Timestamps and comments may vary.)*

!!! tip "Key takeaway"
    Every NSO commit is reversible. Rollback files are your safety net when testing configuration changes.

{% if instructor %}
!!! tip "Instructor"
    **Duration:** +5 min if learners picked wrong rollback file. **FAQs:** No rollback listed — ensure Lab 4 commit completed. **Breaks:** Commit Manager empty — refresh Web UI session.
{% endif %}

## Verification

Confirm the same address from NSO (optional second check):

```bash
source ~/NSO-INSTALL/ncsrc
echo "show running-config devices device xr-1 config cisco-ios-xr:interface GigabitEthernet 0/0/0/0 ipv4 address" | ncs_cli -u admin -C
```

{{ expected_output(landmark="10.1.1.3") }}

*Expected output:*

```text
address 10.1.1.3 255.255.255.0
```

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "Load is greyed out or rollback list is empty.",
  "No prior commit in this session, or wrong NSO instance.",
  "Confirm you committed at least one change in Lab 4; check **Commit Manager** history and lab instructions for the correct instance path."
) }}

{{ common_error(
  "Device still shows 10.1.1.30 after commit.",
  "Wrong rollback selected, or commit not applied to devices.",
  "Re-open the diff in Commit Manager, pick the rollback whose metadata matches the pre-change state, commit again, then re-run Check-Sync / sync-to if your site requires it."
) }}

{{ common_errors_end() }}

