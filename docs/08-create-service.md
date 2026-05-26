---
title: "Lab 8: Create a Service"
chapter: 8

ned_versions:
  - "cisco-iosxr-cli-7.x"
estimated_duration: "30 min"
prerequisites:
  - "Lab 7: Device Groups & Templates completed — you can commit from Configuration Editor and use Service Manager."
learning_objectives:
  - "Generate a python-and-template service package with ncs-make-package."
  - "Model inputs in YANG, map them into a NED XML template, compile, and reload packages."
  - "Deploy a service instance, intentionally drift device config, and re-deploy to reconcile."
idempotent: false
classification: "Cisco Confidential"
---

# Lab 8: Create a Service

{{ lab_safety(variant="intentional_failure") }}

## Learning Objectives

By the end of this lab you will be able to:

- Generate a **python-and-template** service package with **`ncs-make-package`**.
- Define **YANG** inputs, map them into an IOS-XR **XML** template, **compile**, and **reload** packages.
- **Deploy** a service, **intentionally remove** configuration on devices to create drift, then **re-deploy** to restore intent.

## Time Budget

{{ time_budget(total=30, segments=[[7,"Service skeleton"],[19,"Implement & test"],[4,"Verify CLI"]]) }}

## Prerequisites

- [ ] [Lab 7: Device Groups & Templates](07-device-groups-templates.md) completed — you are comfortable with **Commit Manager** and device configuration.
- [ ] NSO instance path matches your environment (examples use **`~/NSO-INSTALL/nso-instance/`**).

## Procedure

Unlike **templates**, **services** attach **lifecycle** semantics: NSO tracks what a service applied and can **detect drift** when someone changes the network outside the service.

### Context: services vs templates

| Feature | Template | Service |
|---------|----------|---------|
| Push config to multiple devices | Yes | Yes |
| Detect if config was changed | No | **Yes** (check-sync) |
| Re-deploy to restore config | No | **Yes** |
| Rollback service-level changes | No | **Yes** |

### Step 1: Inspect ncs-make-package

```bash
ncs-make-package -h 2>&1 | head -n 20
```

{{ expected_output(landmark="python-and-template") }}

*Expected output:*

```text
… python-and-template …
```

*(Use `ncs-make-package -h` without piping if your shell lacks `head`.)*

### Step 2: Create the service skeleton

Run the generator **inside** the instance `packages/` directory so you do not need to move folders afterward.

!!! tip "Run inside `packages/`"
    If you generate elsewhere, copy the resulting folder into `~/NSO-INSTALL/nso-instance/packages/` before compiling.

<!-- lint-skip: no-output -->

```bash
cd ~/NSO-INSTALL/nso-instance/packages/
ncs-make-package --service-skeleton python-and-template STATIC
```

### Step 3: Understand the package layout

Open the project in VS Code and expand the explorer to the **packages** folder.

![VS Code — open the NSO folder](assets/images/lab08/vscode-open-nso-folder.png)

After the script finishes, **`STATIC/`** should resemble:

```text
STATIC/
├── package-meta-data.xml
├── src/
│   └── yang/
│       └── STATIC.yang
├── templates/
│   └── STATIC-template.xml
└── python/
    └── STATIC/
        └── main.py
```

![VS Code explorer showing the STATIC package structure](assets/images/lab08/vscode-package-explorer.png)

**`package-meta-data.xml`** contains the service version and other metadata.

![package-meta-data.xml content](assets/images/lab08/vscode-package-meta-data.png)

### Step 4: Capture XML with commit dry-run

Build the target IOS-XR static route in the NSO CLI, then export **XML** with **`commit dry-run outformat xml`** — **do not** leave the candidate committed.

<!-- lint-skip: no-output -->

```bash
ncs_cli -Cu admin
```

Example session (prompts may differ):

```text
admin@ncs# config
admin@ncs(config)# devices device xr-1 config
admin@ncs(config-config)# router static
admin@ncs(config-static)# address-family ipv4 unicast
admin@ncs(config-static-afi)# 11.11.11.11/32 10.1.1.2 metric 100 description "set by NSO"
admin@ncs(config-static-afi)# commit dry-run outformat xml
```

You should see XML shaped like the fragment below (namespaces may vary by NED build):

```xml
<devices xmlns="http://tail-f.com/ns/ncs">
  <device>
    <name>xr-1</name>
    <config>
      <router xmlns="http://tail-f.com/ned/cisco-ios-xr">
        <static>
          <address-family>
            <ipv4>
              <unicast>
                <routes-ip>
                  <net>11.11.11.11/32</net>
                  <address>10.1.1.2</address>
                  <metric2>
                    <metric>100</metric>
                  </metric2>
                  <description>set by NSO</description>
                </routes-ip>
              </unicast>
            </ipv4>
          </address-family>
        </static>
      </router>
    </config>
  </device>
</devices>
```

!!! warning "Do not commit the dry-run candidate"
    Exit without committing the exploratory static route — answer **`no`** if asked to commit, or `end` / `exit` per your CLI help.

```text
Uncommitted changes found, commit them? [yes/no/CANCEL] no
```

### Step 5: Populate the service template

The generated skeleton includes an **XML template** and a **YANG model** — you will edit both.

![Default STATIC-template.xml content](assets/images/lab08/vscode-xml-template-file.png)

![Default STATIC.yang content](assets/images/lab08/vscode-yang-file.png)

Copy only the **`router`** subtree (inside **`<config>`**) into **`STATIC-template.xml`**:

```xml
<router xmlns="http://tail-f.com/ned/cisco-ios-xr">
  <static>
    <address-family>
      <ipv4>
        <unicast>
          <routes-ip>
            <net>11.11.11.11/32</net>
            <address>10.1.1.2</address>
            <metric2>
              <metric>100</metric>
            </metric2>
            <description>set by NSO</description>
          </routes-ip>
        </unicast>
      </ipv4>
    </address-family>
  </static>
</router>
```

### Step 6: Add YANG variables

Replace literals with service inputs. Typical leaves:

1. **Destination prefix** (for example `11.11.11.11/32`)
2. **Forwarding address** (for example `10.1.1.2`)
3. **Metric** (default **100**)
4. **Description** (default **`set by NSO`**)

![Four variables identified: destination prefix, forwarding address, metric, description](assets/images/lab08/slide-variables-identification.png)

#### Update `STATIC-template.xml`

Reference those leaves with your template engine’s variable syntax (for example `{$DEST}` / `{$CONTEXT}` patterns — follow the generated skeleton comments).

![XML template with variable placeholders](assets/images/lab08/slide-xml-with-variables.png)

#### Update `STATIC.yang`

Make **`dest-prefix`** and **`fwd-address`** mandatory; give **`metric`** and **`description`** defaults (exact syntax follows your YANG tutorial).

![YANG model with leaf definitions and defaults](assets/images/lab08/slide-yang-with-variables.png)

```yang
// replace with your own stuff here
leaf dest-prefix {
    type inet:ipv4-prefix;
    mandatory true;
}
leaf fwd-address {
    type inet:ipv4-address;
    mandatory true;
}

leaf metric {
    type uint16;
    default "100";
}

leaf description {
    type string;
    default "set by NSO";
}
```

### Step 7: Compile the package

```bash
cd ~/NSO-INSTALL/nso-instance/packages/STATIC/src
make
```

{{ expected_output(landmark="STATIC.fxs") }}

*Expected output:*

```text
… ncsc … -o ../load-dir/STATIC.fxs yang/STATIC.yang
```

*(Warnings policy depends on your flags; **`--fail-on-warnings`** may stop the build if YANG has issues.)*

### Step 8: Reload packages

1. Web UI → **ncs:packages → Actions → Reload**.
2. Confirm **result** is **true**.

![Packages reload — result true](assets/images/lab08/webui-packages-reload-true.png)

3. Verify package **STATIC** appears.

![STATIC package listed after reload](assets/images/lab08/webui-packages-static-listed.png)

### Step 9: Deploy the service instance

1. **Homepage → Services**.


2. Select the **STATIC** service.

![Select the STATIC service](assets/images/lab08/webui-services-static-select.png)

3. **+ Add service** — click the **+** button.

![Click + Add service](assets/images/lab08/webui-services-add-instance.png)

4. Name it (for example **`static-11.11.11.11`**) and fill **dest-prefix**, **fwd-address**.

![Enter service instance name and mandatory fields](assets/images/lab08/webui-services-instance-name.png)

Service created — now attach devices.

![Service instance created](assets/images/lab08/webui-services-instance-created.png)

5. Attach devices **xr-1** and **xr-2** (defaults for metric/description if shown).

![Add devices to the service instance](assets/images/lab08/webui-services-add-devices.png)

6. **Commit Manager → config** — inspect diff; use **native config** if offered.

![Commit Manager diff for the service deployment](assets/images/lab08/webui-service-commit-diff.png)

![Native config view showing CLI commands NSO will send](assets/images/lab08/webui-service-native-config.png)

7. **Commit**.

### Step 10: Test lifecycle (intentional drift)

1. **Service Manager** — service should be **green** / in-sync after commit.

![Service check-sync — green (in-sync) after deploy](assets/images/lab08/webui-service-check-sync-green.png)

2. **Simulate a problem (required for this lab):** on **each** device, **Device Manager → Edit Config**, delete the **static route** the service applied.

![Device Manager — select and delete the static route](assets/images/lab08/webui-device-delete-static.png)

3. **Commit** the deletion on the device context.

![Commit the device-level deletion](assets/images/lab08/webui-device-delete-commit.png)

4. Return to **Service Manager → Check-Sync** — expect a **red** / out-of-sync indication.

![Service check-sync — red (out-of-sync) after device drift](assets/images/lab08/webui-service-check-sync-red.png)

![Out-of-sync detail showing the drift](assets/images/lab08/webui-service-check-sync-red-detail.png)

5. Run **Re-deploy** on the service — NSO should push intent back to devices until the service is **green** again.

![Select Re-deploy from the service actions](assets/images/lab08/webui-service-redeploy.png)

![Service check-sync — green again after re-deploy](assets/images/lab08/webui-service-redeploy-green.png)

!!! tip "Key takeaway"
    Services are **self-healing** for configuration they own: drift is visible, and **re-deploy** reapplies the service’s intended configuration.

{% if instructor %}
!!! tip "Instructor"
    **Duration:** allow +15 min for compile errors. **FAQs:** Wrong NED namespace in template — match `ncs-make-package` skeleton. **Breaks:** Package reload false — check `packages/STATIC/load-dir` and `make` output.
{% endif %}

## Verification

On **xr-1**, confirm the static route exists after re-deploy (documentation address — use yours):

<!-- lint-skip: no-output -->

```bash
ssh admin@172.30.0.2
(admin@172.30.0.2) Password: (password = cisco123)
```

```cli
show run router static
```

{{ expected_output(landmark="11.11.11.11") }}

*Expected output:*

```text
router static
 address-family ipv4 unicast
  11.11.11.11/32 10.1.1.2 description "set by NSO" metric 100
```

## Common Errors

{{ common_errors_start() }}

{{ common_error(
  "make fails or STATIC.fxs is missing after compile.",
  "YANG error, wrong NED namespace in template, or wrong working directory.",
  "Run `make clean` if present, fix YANG/XML per compiler errors, rebuild from `STATIC/src`."
) }}

{{ common_error(
  "Service stays red after re-deploy or devices reject the route.",
  "Overlapping static routes, VRF mismatch, or device not in service device list.",
  "Verify service instance targets **xr-1** / **xr-2**, check device trace logs, roll back last service commit if needed."
) }}

{{ common_errors_end() }}

!!! warning "Rollback"
    To remove this lab’s **STATIC** package and instance (destructive — coordinate with your class):

    ```bash
    ncs --stop 2>/dev/null || true
    rm -rf ~/NSO-INSTALL/nso-instance/packages/STATIC
    ncs
    ```

    Then **Reload packages** in the Web UI and confirm **STATIC** is gone.

If re-deploy cannot clear drift or the service model is inconsistent, use **Commit Manager** rollbacks first, then restore the VM snapshot if you need a clean start.
