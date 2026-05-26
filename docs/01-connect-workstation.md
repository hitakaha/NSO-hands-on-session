---
title: "Lab 1: Connect to the Workstation"
chapter: 1

ned_versions:
  - "cisco-ios-cli-6.x"
  - "cisco-iosxr-cli-7.x"
estimated_duration: "10 min"
prerequisites:
  - "Access to the hosted lab portal and Remote Access (VM console) for this workbook."
learning_objectives:
  - "Connect to the Ubuntu lab desktop through the hosted Remote Access console."
  - "Open Visual Studio Code and use the integrated terminal on linux-host."
  - "Verify workstation identity using basic shell commands."
idempotent: true
classification: "Cisco Confidential"
---

# Lab 1: Connect to the Workstation

## Learning Objectives

By the end of this lab you will be able to:

- Connect to the Ubuntu lab desktop through the hosted Remote Access console.
- Open Visual Studio Code and use the integrated terminal on linux-host.
- Verify workstation identity using basic shell commands.

## Time Budget

{{ time_budget(total=10, segments=[[3,"Console & desktop"],[5,"VS Code & terminal"],[2,"Verify shell"]]) }}

## Prerequisites

- [ ] You can sign in to the hosted lab environment and open **Remote Access** (or equivalent) for this workbook.
- [ ] You have a modern browser; pop-up blockers are disabled or allow-listed for the lab portal if your site requires it.

## Procedure

You will use the **linux-host** Ubuntu desktop and its integrated terminal for all following labs. Choose **Ubuntu 24.04 Desktop** unless your facilitator directs otherwise.

### Step 1: Open the lab VM console

1. From the lab environment, select **Ubuntu 24.04 Desktop** (recommended) or **Win11** if you must use Windows for this session.
2. Open **VM Console** from the **Remote Access** menu (wording may vary slightly by platform).

![Lab portal — select the VM and open VM Console from Remote Access](assets/images/01/lab-portal-vm-console.png)

3. On Windows, if you see “You’re almost done setting up your PC,” choose **Remind me in 3 days** to reach the desktop.

![Windows desktop after initial setup prompt](assets/images/01/windows-desktop-setup.png)

Wait until you see the desktop background and can move the pointer inside the VM.

### Step 2: Orient yourself on the desktop

Alternatively, if you chose **Ubuntu 24.04 Desktop**, you will see a desktop similar to this:

![Ubuntu 24.04 Desktop — VM Console view](assets/images/01/ubuntu-desktop-vm-console.png)

### Step 3: Open Visual Studio Code and the integrated terminal

1. Open **Visual Studio Code** from the applications menu or the dock.
2. Open the integrated terminal (**Terminal → New Terminal** or the shortcut shown in your environment).

![VS Code with the integrated terminal open](assets/images/01/vscode-terminal-open.png)

3. Stay in this terminal for command examples in later labs.

### Step 4: Confirm the workstation hostname

Run:

```bash
hostname
```

{{ expected_output(landmark="linux-host") }}

*Expected output:*

```text
xrd-host
```

If the name differs, ask your facilitator—some environments use a different label, but the workflow is the same.

{% if instructor %}
!!! tip "Instructor"
    **Duration:** ~12 min with a warm VPN. **FAQs:** Black console—refresh VM console; no VS Code—Activities search. **Breaks:** Stale Remote Access—new private window.
{% endif %}

## Verification

Confirm you are on **xrd-host** and the shell is responsive. Run these in order in the same terminal:

```bash
hostname
whoami
pwd
```

{{ expected_output(landmark="linux-host") }}

*Expected output:*

```text
xrd-host
cisco
/home/cisco
```

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "Black or frozen VM console after Remote Access.",
  "Browser session timed out, GPU acceleration glitch, or console tab lost focus.",
  "Refresh the Remote Access page, close other heavy tabs, and reopen VM Console. If it persists, restore the VM snapshot."
) }}

{{ common_error(
  "Integrated terminal in VS Code does not open or closes immediately.",
  "VS Code started before the desktop session finished loading, or extension host crashed.",
  "Quit VS Code fully and reopen from the menu. If needed, use an external terminal app temporarily and continue Lab 2 from there."
) }}

{{ common_errors_end() }}

If the desktop or console is unusable after these steps, restore the lab VM snapshot and retry.
