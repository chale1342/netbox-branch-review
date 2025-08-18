# NetBox Branch Review — Example


## 1) Create a Change Request
Only Title and Summary are needed; Requested by is optional/auto.

![Create request](./images/cr-request.png)

## 2) Browse the list
See status and who approved.

![Change Requests list](./images/cr-list.png)

## 3) Approve
Click Approve (peer approval may be required depending on config).

![Approved](./images/cr-approved.png)

## 4) Merge / Implement
When approved and a branch is attached, select Merge / Implement.

![Merged](./images/cr-merged.png)

## Optional: Branch view
If you work directly with branches, you’ll see it merged as well.

![Branch merged](./images/branch-merged.png)

Tips
- Configure `require_two_approvals` and `allow_self_full_approval` in `PLUGINS_CONFIG`.
- The Branching plugin validator can enforce approval before merges.
