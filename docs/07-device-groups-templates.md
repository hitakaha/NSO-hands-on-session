---
title: "Lab 7: Device Groups & Templates"
chapter: 7

ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "25 min"
prerequisites:
  - "Lab 6: Out-of-Band Sync completed — xr-1 and xr-2 are in sync with NSO."
learning_objectives:
  - "Create a device group that contains multiple managed devices."
  - "Author a device template with NED-scoped settings (for example DNS name-servers)."
  - "Apply a template to a device group and verify configuration on a device CLI."
idempotent: true
classification: "Cisco Confidential"
---

# Lab 7: Device Groups & Templates

## Learning Objectives

By the end of this lab you will be able to:

- Create a **device group** that contains **xr-1** and **xr-2**.
- Define a **device template** with IOS-XR DNS settings.
- Run **Apply-Template** for the group and verify **DNS** configuration on a device.

## Time Budget

{{ time_budget(total=25, segments=[[10,"Device group"],[15,"Template & apply"]]) }}

## Prerequisites

- [ ] [Lab 6: Out-of-Band Sync](06-out-of-band-sync.md) completed — both devices are **in-sync** and reachable.
- [ ] You can open **Configuration Editor** and **Commit Manager** as **admin**.

## Procedure

Device **groups** and **templates** let you push configuration to **multiple** devices with one action.

### Step 1: Create a device group

1. Go to **Devices → Device groups**.
2. Click **+ Add device group**.
3. Name it **`ios-xr-devices`** and click **Create**.

![Enter a group name like ios-xr-devices](assets/images/lab07/webui-device-group-create-name.png)

4. Select **xr-1** and **xr-2**, then **+ Add to device group**.

![Select devices to add to the group](assets/images/lab07/webui-device-group-add-devices.png)

5. Click **Create device group**.

Both devices should appear in **`ios-xr-devices`**.

![Device group ios-xr-devices created with both devices](assets/images/lab07/webui-device-group-created.png)

### Step 2: Create a device template

1. Open **Configuration Editor**.
2. Select the **ncs:devices** module and click **Edit config**.

![Configuration Editor showing the ncs:devices module](assets/images/lab07/webui-config-editor-devices.png)

3. In the **template** tile, click **+** add name 'set-dns'.

![Click the + button to create a new template](assets/images/lab07/webui-template-create-plus.png)

4. Choose NED **cisco-iosxr**, then **Confirm**.

![Select the IOS-XR NED for the template](assets/images/lab07/webui-template-ned-select.png)

5. Open the NED subtree to edit template content.

![NED config subtree inside the template](assets/images/lab07/webui-template-ned-config.png)

### Step 3: Configure DNS in the template

1. Navigate to **Domain** (path may read **domain** / **Domain name** depending on UI skin).

![Search for the Domain configuration inside the NED](assets/images/lab07/webui-template-domain-search.png)

2. Add a **domain name** and **name-server** IP (example: **`2.2.2.2`** — documentation-style resolver).

![Fill in the domain name and name-server fields](assets/images/lab07/webui-template-domain-fields.png)

### Step 4: Review and commit

1. Open **Commit Manager** and review the diff — you should see the new **device group** and **template** objects.

![Commit Manager diff showing device-group and template configuration](assets/images/lab07/webui-template-commit-diff.png)

![Commit detail with the template and device group definitions](assets/images/lab07/webui-template-commit-detail.png)

2. **Commit**.

### Step 5: Apply the template to the group

1. In **Configuration Editor → ncs:devices**, open the device group **`ios-xr-devices`**.
2. Click **Actions**.

![Device group Actions menu in the Configuration Editor](assets/images/lab07/webui-device-group-actions.png)

3. Click **Apply-Template**.

![Apply-Template button](assets/images/lab07/webui-apply-template-button.png)

4. Select your template name (scroll if needed).

![Select the template name to apply](assets/images/lab07/webui-apply-template-select.png)

5. Run **Apply-Template**.

The action result should show **ok** for each member device.

![Apply-Template result — ok for both xr-1 and xr-2](assets/images/lab07/webui-apply-template-result.png)

!!! info "Templates vs services"
    Templates are flexible but lack **service lifecycle** semantics. Uncontrolled edits on devices can drift from the template intent — **services** (Lab 8) add structure and reconciliation.

{% if instructor %}
!!! tip "Instructor"
    **Duration:** +10 min if Apply-Template fails ACL/NACM. **FAQs:** Template not listed — commit the template first. **Breaks:** Partial apply — check per-device sync then rollback last commit.
{% endif %}

## Verification

On **xr-1**, confirm DNS settings from the template:

<!-- lint-skip: no-output -->

```bash
ssh admin@172.30.0.2
(admin@172.30.0.2) Password: (password = cisco123)
```

```cli
show run domain
```

{{ expected_output(landmark="name-server") }}

*Expected output:*

```text
domain name-server 2.2.2.2
```

![Device CLI showing DNS domain configuration applied via template](assets/images/lab07/terminal-device-dns-verify.png)

*(Additional `domain name` lines may appear if you set them in the template.)*

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "Apply-Template returns failed or only one device updates.",
  "Authgroup mapping, device lock, or template path not committed.",
  "Verify both devices in the group share credentials; check Commit Manager for errors, then sync-from on failing device."
) }}

{{ common_error(
  "show run domain is empty after a successful apply.",
  "Template targeted wrong NED branch or DNS not under domain in your IOS-XR model.",
  "Re-open the template in Configuration Editor, confirm **Domain** leaves exist in the diff, commit, and re-run Apply-Template."
) }}

{{ common_errors_end() }}

If **apply-template** fails for all devices or leaves partial state, roll back the last commits or restore the VM snapshot.
