---
title: "Lab 6: Out-of-Band Sync"
chapter: 6

ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "20 min"
prerequisites:
  - "Lab 5: Rollbacks completed — NSO and devices are in a known, in-sync state."
learning_objectives:
  - "Create a configuration change directly on a device (out-of-band) without using NSO."
  - "Use Check-Sync in the Web UI to detect drift between the device and the NSO CDB."
  - "Choose Sync-To or Sync-From to reconcile drift and verify the result on the device."
idempotent: true
classification: "Cisco Confidential"
---

# Lab 6: Out-of-Band Sync

## Learning Objectives

By the end of this lab you will be able to:

- Create a configuration change **directly on xr-1** (out-of-band) without using NSO.
- Run **Check-Sync** in the Web UI to detect configuration drift.
- Use **Sync-To** to align the device with NSO and verify the loopback is removed.

## Time Budget

{{ time_budget(total=20, segments=[[10,"Out-of-band change"],[10,"Detect & reconcile"]]) }}

## Prerequisites

- [ ] [Lab 5: Rollbacks](05-rollbacks.md) completed — **Check-Sync** should be **green** for **xr-1** before you start.
- [ ] You can SSH from **linux-host** to **xr-1** (examples use **172.30.0.2**).

## Procedure

One of NSO’s core workflows is detecting changes made **on the device** that did not go through NSO — **out-of-band** configuration.

### Step 1: Create an out-of-band change on xr-1

SSH to **xr-1** and configure **Loopback100** on the device CLI (not through NSO).

<!-- lint-skip: no-output -->

```bash
ssh admin@172.30.0.2
(admin@172.30.0.2) Password: (password = cisco123)
```

At the XR prompt, use a configuration session like this (prompts and timestamps will match your session):

```text
RP/0/RP0/CPU0:xr-1#configure terminal
RP/0/RP0/CPU0:xr-1(config)#interface Loopback 100
RP/0/RP0/CPU0:xr-1(config-if)#description out-of-band change
RP/0/RP0/CPU0:xr-1(config-if)#commit
RP/0/RP0/CPU0:xr-1(config-if)#end
```

### Step 2: Verify the loopback on the device

```cli
show run interface Loopback 100
```

{{ expected_output(landmark="Loopback100") }}

*Expected output:*

```text
interface Loopback100
 description out-of-band change
!
```

### Step 3: Detect drift in NSO

In the NSO Web UI, run **Check-Sync** on **xr-1**.

![Check-Sync result — xr-1 is out-of-sync (transaction hash mismatch)](assets/images/lab06/webui-check-sync-out-of-sync.png)

!!! danger "Out-of-sync alert"
    NSO typically shows a **red** indicator because the device differs from the CDB. Open **Compare-config** to see the out-of-band change.

![Compare config shows Loopback 100 with description "out-of-band change" added on the device](assets/images/lab06/webui-compare-config-loopback.png)

### Step 4: Resolve with Sync-To vs Sync-From

| Option | Action | Result |
|--------|--------|--------|
| **Sync-From** | Pull device config into NSO | NSO **accepts** the out-of-band change |
| **Sync-To** | Push NSO’s config to the device | Device **matches** NSO (drops OOB change) |

To **remove** the loopback and match the prior NSO-known state, use **Sync-To**.

### Step 5: Execute Sync-To

1. Select **xr-1** in the Web UI.
2. Open the actions menu and choose **Sync to**.

![Device actions dropdown with Sync to highlighted](assets/images/lab06/webui-device-actions-sync-to.png)

### Step 6: Verify reconciliation

Run **Check-Sync** again — both devices should show **in-sync**.

![Check-Sync after Sync-To — both xr-1 and xr-2 report in-sync](assets/images/lab06/webui-check-sync-both-in-sync.png)

On the device:

```cli
show run interface Loopback 100
```

{{ expected_output(landmark="No such configuration") }}

*Expected output:*

```text
% No such configuration item(s)
```

The Loopback **100** configuration is gone — NSO restored the device to its known-good state.

!!! tip "Key takeaway"
    Use **check-sync** regularly; pair it with **sync-from** or **sync-to** deliberately — **sync-from** ingests reality, **sync-to** enforces the NSO-intended configuration.

{% if instructor %}
!!! tip "Instructor"
    **Duration:** +10 min if Sync-To blocks on locks. **FAQs:** Red but empty diff — refresh device session. **Breaks:** Stuck sync — restart `ncs` only as last resort; prefer restoring the VM snapshot.
{% endif %}

## Verification

Confirm **xr-1** is clear of Loopback **100** and NSO agrees:

1. In the Web UI, **Check-Sync** for **xr-1** is **green**.
2. On the device CLI:

```cli
show run interface Loopback 100
```

{{ expected_output(landmark="No such configuration") }}

*Expected output:*

```text
% No such configuration item(s)
```

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "Check-Sync stays red after Sync-To or shows a looping diff.",
  "Concurrent edits, partial sync, or SSH session left in config mode on the device.",
  "Close extra sessions, run **Check-Sync** again, then **Sync-To** once; capture Compare-config for the instructor. Restore the VM snapshot if stuck."
) }}

{{ common_error(
  "Loopback still present after Sync-To.",
  "Wrong device selected, or sync targeted a different NSO instance.",
  "Confirm **xr-1** address and authgroup; re-run **Sync-To** and verify with `show run interface Loopback 100` on the device."
) }}

{{ common_errors_end() }}
