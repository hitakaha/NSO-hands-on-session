---
title: "Lab 9: RBAC Access Control"
chapter: 9

ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "30 min"
prerequisites:
  - "Labs 1–7 completed — devices xr-1 and xr-2 exist, and you can edit NACM as admin."
learning_objectives:
  - "Create a local NSO user and map it through an authgroup to device credentials."
  - "Define NACM groups and rule-lists that target configuration subtrees by XPath."
  - "Validate allow/deny behavior by switching between admin and a restricted user."
idempotent: true
classification: "Cisco Confidential"
---

# Lab 9: RBAC Access Control

## Learning Objectives

By the end of this lab you will be able to:

- Create a local NSO user and attach it to device credentials through an **authgroup**.
- Configure **NACM** groups, rule-lists, and rules that target paths with **XPath**.
- Log in as a restricted user and confirm allowed vs denied actions in the Web UI.

## Time Budget

{{ time_budget(total=30, segments=[[10,"Users & authgroups"],[15,"NACM rules"],[5,"Broaden rule"]]) }}

## Prerequisites

- [ ] You can log in to the NSO Web UI as **admin** and open **Configuration Editor** for **aaa**, **nacm**, and **devices**.
- [ ] Device definitions for **xr-1** / **xr-2** use management addresses consistent with your lab (examples use **198.51.100.2** for **xr-1** in XPath samples).

## Procedure

NSO combines **AAA users**, **authgroups** (device credential mapping), and **NACM** (northbound access rules) for fine-grained control.

### Step 1: Create a read-only test user

1. Open **Configuration Editor → aaa:aaa**.

![Configuration Editor showing the aaa:aaa module](assets/images/lab09/webui-aaa-module.png)

2. Navigate to **authentication → users**, click **Edit config**, then **+** to add a user.

![Click + to add a new user under authentication/users](assets/images/lab09/webui-aaa-users-add.png)

3. Create **`read_user`** (password per your lab policy).

![Create the read_user account](assets/images/lab09/webui-aaa-create-read-user.png)

4. **Commit**.

You can log out and confirm login as **`read_user`** (limited until NACM is configured).

![Log in as read_user to verify the account works](assets/images/lab09/webui-login-read-user.png)

### Step 2: Map the user through an authgroup

As **`read_user`**, open **Device Manager** — note that **ping** fails because the user has no authgroup mapping yet.

![Device Manager as read_user — limited access](assets/images/lab09/webui-device-manager-read-user.png)

![Ping fails — read_user is not mapped to any authgroup](assets/images/lab09/webui-ping-no-authgroup.png)

Log back in as **admin** to fix this:

1. Open **Configuration Editor → ncs:devices → authgroup** (select the group your devices use, often **`XR`**).

![Select the XR authgroup](assets/images/lab09/webui-authgroup-select-xr.png)

2. Inside the authgroup, locate the **umap** section (maps NSO users to device credentials).

![Umap section inside the XR authgroup](assets/images/lab09/webui-authgroup-umap.png)

3. Add **`read_user`** with **remote-name** / **remote-password** matching device login (**`admin`** / **`cisco123`** in many labs).

![Add read_user to the XR authgroup umap](assets/images/lab09/webui-authgroup-add-read-user.png)

![Set remote credentials for read_user](assets/images/lab09/webui-authgroup-remote-creds.png)

4. **Commit**.

Log in as **`read_user`** and open **Device Manager** — you should now reach **connect**, **ping**, and **check-sync**.

![Operations available to read_user after authgroup mapping](assets/images/lab09/webui-authgroup-operations.png)

### Step 3: Create a NACM group and rule-list

1. Log in as **admin**.
2. Open **Configuration Editor → nacm:nacm**.

![NACM module in the Configuration Editor](assets/images/lab09/webui-nacm-module.png)

The NACM module contains **rule-list** and **groups** sections.

![NACM rule-list and groups overview](assets/images/lab09/webui-nacm-rule-list-groups.png)

3. Create **`read_group`**.

![Create the read_group](assets/images/lab09/webui-nacm-create-read-group.png)

4. Assign **group-id** (for example **`1`**) and add user **`read_user`**.

![Set group-id and add read_user to the group](assets/images/lab09/webui-nacm-group-id-user.png)

5. Under **rule-lists**, create **`read_rule`**.

![Create the read_rule rule-list](assets/images/lab09/webui-nacm-create-read-rule.png)

6. Attach **`read_group`** so all rules in the list apply to that membership.

![Attach read_group to the read_rule rule-list](assets/images/lab09/webui-nacm-rule-attach-group.png)

### Step 4: Discover XPath targets

Use the NSO CLI to print XPath forms of configuration (paths vary slightly by release):

```bash
source ~/NSO-INSTALL/ncsrc
echo "show devices device | display xpath" | ncs_cli -u admin -C
```

{{ expected_output(landmark="devices/device") }}

*Expected output:*

```text
/devices/device[name='xr-1']/…
/devices/device[name='xr-2']/…
```

*(Truncated — you need the `/devices/device[...]` prefixes for rules.)*

![CLI output showing XPath form of device configuration](assets/images/lab09/terminal-xpath-display.png)

For deeper paths:

<!-- lint-skip: no-output -->

```bash
source ~/NSO-INSTALL/ncsrc
echo "show configuration devices device xr-1 | display xpath" | ncs_cli -u admin -C
```

*Expected output (illustrative — addresses follow your lab):*

```text
/devices/device[name='xr-1']/address 198.51.100.2
/devices/device[name='xr-1']/authgroup XR
/devices/device[name='xr-1']/device-type/cli/ned-id cisco-iosxr-cli-7.x
```

!!! info "Access operations"
    Use the UI help on **access-operations** to see **create**, **update**, **delete**, **exec**, and related keywords for your release.

### Step 5: Create a deny rule for domain configuration on xr-1

Inside the rule-list you have two options: **cmdrule** (command authorization) and **rule** (data/rpc authorization).

![cmdrule vs rule options in the rule-list](assets/images/lab09/webui-nacm-cmdrule-vs-rule.png)

1. Inside **`read_rule`**, add a rule to deny sync-from or domain access.

![Add a deny rule targeting sync-from](assets/images/lab09/webui-nacm-deny-sync-from.png)

2. In the rule **data-node**, set the **path** using the XPath from Step 4:
   `/devices/device[name='xr-1']/config/cisco-ios-xr:domain`
3. **Action:** `deny`
4. **Access-operations:** `create`, `update`, `delete`, `exec` (adjust to your NACM schema).

![Rule with XPath path and deny action configured](assets/images/lab09/webui-nacm-rule-xpath-deny.png)

Use the **info** button on **access-operations** to see all available keywords.

![Access-operations info showing available keywords](assets/images/lab09/webui-nacm-access-operations-info.png)

5. **Commit**.

### Step 6: Test as read_user

1. Log out, then log in as **`read_user`**.
2. Open **Device Manager**.

You should observe:

- **sync-from** may be hidden or disabled (depending on remaining default rules).

![read_user Device Manager — sync-from is not available](assets/images/lab09/webui-read-user-no-sync-from.png)

- On **xr-1**, **domain** configuration is not visible or not editable.

![xr-1 config as read_user — domain is hidden by the NACM rule](assets/images/lab09/webui-read-user-xr1-no-domain.png)

- On **xr-2**, **domain** may still appear if the rule only names **xr-1**.

![xr-2 still shows domain because the rule targets only xr-1](assets/images/lab09/webui-read-user-xr2-still-domain.png)

### Step 7: Broaden the rule to all devices

1. Log in as **admin**.
2. Change the rule path from:
   ```text
   /devices/device[name='xr-1']/config/cisco-ios-xr:domain
   ```
   to:
   ```text
   /devices/device/config/cisco-ios-xr:domain
   ```

![Update the rule path to target all devices](assets/images/lab09/webui-nacm-broadened-path.png)

3. **Commit**.

Log in as **`read_user`** again — **domain** should be hidden on **all** managed devices covered by the rule.

![All devices — domain configuration is hidden for read_user](assets/images/lab09/webui-read-user-all-no-domain.png)

!!! tip "Key takeaway"
    NACM rules target **XPath** expressions — from entire subtrees down to single leaves — to control who can see or change configuration.

{% if instructor %}
!!! tip "Instructor"
    **Duration:** +15 min if learners mis-type XPath. **FAQs:** Still admin-equivalent — clear browser session. **Breaks:** Lockout — use admin + Commit Manager rollback for `nacm` changes.
{% endif %}

## Verification

Confirm **`read_user`** still exists (admin session):

```bash
source ~/NSO-INSTALL/ncsrc
echo "show configuration aaa authentication users user read_user" | ncs_cli -u admin -C
```

{{ expected_output(landmark="read_user") }}

*Expected output:*

```text
user read_user {
```

*(Additional password / key lines may follow — you only need to see the **`read_user`** stanza.)*

Confirm NACM rules in the Web UI under **Configuration Editor → nacm:nacm** — **`read_rule`** should list **`deny-config-domain`**. Optional CLI (output varies):

<!-- lint-skip: no-output -->

```bash
source ~/NSO-INSTALL/ncsrc
echo "show configuration nacm nacm rule-list read_rule" | ncs_cli -u admin -C
```

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "read_user sees the same UI as admin or changes still apply after deny.",
  "Session cache, wrong user, or rule path typo / wrong NACM group attachment.",
  "Log out fully, clear site data if needed, re-check **groups** ↔ **read_user** mapping and XPath spelling (including namespace prefix)."
) }}

{{ common_error(
  "ncs_cli XPath commands return errors or empty.",
  "Wrong `-u` user, environment not sourced, or display xpath not supported in your build.",
  "Run `source ~/NSO-INSTALL/ncsrc` first; use **Configuration Editor** copy-path features as a fallback."
) }}

{{ common_errors_end() }}

If you lock yourself out or rules conflict, log in as **admin** and revert the last **NACM** commits in **Commit Manager**.

## What's Next

Lab 9 closes the **Day 2 morning** track: you now have NSO operating with proper user, authgroup, and NACM separation — the foundation a production deployment needs.

The **Day 2 afternoon** session shifts to **NSO 6.7** and its new **Model Context Protocol (MCP) server**. In [Lab 10: NSO MCP — Setup and First Client](10-nso-mcp-setup.md), you will spin up NSO 6.7 in the dCloud "NSO 6.7 MCP" scenario, expose it via MCP, and drive it from a web-based natural-language client — then in [Lab 11](11-nso-mcp-services-bgp.md), use that same client to configure BGP through a custom service package.
