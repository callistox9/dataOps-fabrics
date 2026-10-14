# DataOps for Microsoft Fabric

This repository is a starter kit for managing Microsoft Fabric workspace items as code and promoting them through development, test, and production environments. It includes Azure DevOps pipeline examples, deployment and validation scripts, environment-specific configuration, and branching-strategy diagrams.

> **Status:** This repository is a template, not a ready-to-run deployment. Add your Fabric items and environment configuration, then resolve the pipeline path/name mismatches listed under [Pipeline setup notes](#pipeline-setup-notes).

## What’s included

| Path | Purpose |
| --- | --- |
| [`ado-pipelines/azure-pipelines.yml`](ado-pipelines/azure-pipelines.yml) | Azure Pipelines example for validation and deployments to Test and Prod |
| [`ado-pipelines/promotion-pipeline.yml`](ado-pipelines/promotion-pipeline.yml) | Manually triggered fast-forward promotion from Dev to Test, or from a tested tag to Prod |
| [`ado-pipelines/templates/deploy.yml`](ado-pipelines/templates/deploy.yml) | Reusable deployment job: provenance check, Fabric publish, smoke test, and success tag |
| [`ado-pipelines/scripts/deploy.py`](ado-pipelines/scripts/deploy.py) | Publishes supported Fabric items with `fabric-cicd` |
| [`ado-pipelines/scripts/validate.py`](ado-pipelines/scripts/validate.py) | Checks environment replacements, workspace content, and basic secret patterns |
| [`ado-pipelines/scripts/smoke_tests.py`](ado-pipelines/scripts/smoke_tests.py) | Compares repository item definitions with items in a Fabric workspace |
| [`ado-pipelines/workspace/parameter.yml`](ado-pipelines/workspace/parameter.yml) | Example environment-specific value replacements |
| [`branching-strategy/`](branching-strategy/) | Editable draw.io diagrams, HTML renderings, and a PDF illustrating branching and workspace promotion |
| [`pre-commits/Readme.md`](pre-commits/Readme.md) | Example guidance for setting up local pre-commit hooks |

## Promotion model

The pipeline examples use three Git branches and three corresponding Fabric environments:

1. Develop and validate Fabric items in the Dev workspace.
2. Promote `dev` to `test` using the promotion pipeline. The promotion is a fast-forward only; it fails if the target branch has diverged.
3. Deploy `test` to the Test workspace. The deployment checks that its commit is an ancestor of `dev`.
4. After a successful Test deployment and smoke test, the pipeline creates a `tested-YYYYMMDD-<commit>` tag.
5. Promote a selected `tested-` tag to `prod`, then deploy to the Prod workspace. Production deployment requires a tested tag and can be gated by approvals on the configured Azure DevOps environment.
6. After a successful Prod deployment and smoke test, the pipeline creates a `released-YYYYMMDD-<commit>` tag.

The branching-strategy diagrams are visual references; check their branch names against the `dev`, `test`, and `prod` names used by the pipeline YAML before adopting them.

## Prerequisites

- An Azure DevOps project with this repository and permission to run Azure Pipelines.
- Microsoft Fabric workspaces for Dev, Test, and Prod.
- Azure DevOps service connections with appropriate Fabric permissions:
  - `sc-fabric-test`
  - `sc-fabric-prod`
- Azure DevOps variable groups named `fabric-test` and `fabric-prod`, each defining `WORKSPACE_ID` for its target workspace.
- Python 3.12 on the pipeline agent.
- Fabric item definitions synced or exported into `ado-pipelines/workspace/`.

Use a service principal or managed identity through Azure DevOps service connections for pipeline authentication. Do not commit credentials, access tokens, or other secrets to the repository.

## Configure the template

1. Add your Fabric item folders and definitions under `ado-pipelines/workspace/`.
2. Edit `ado-pipelines/workspace/parameter.yml`. Replace the example `<dev-lakehouse-id>`, `<test-lakehouse-id>`, and `<prod-lakehouse-id>` values with the corresponding IDs. The replacement environment keys must be `TEST` and `PROD`.
3. Configure the Azure DevOps service connections, variable groups, workspace IDs, and deployment environments to match your organization.
4. Review `DEFAULT_ITEM_TYPES` in `ado-pipelines/scripts/deploy.py`; include only item types supported by your installed `fabric-cicd` version and used by your project.
5. Review the validation patterns and item scope for your organization. The repository secret check is explicitly a baseline, not a replacement for a dedicated secret scanner.
6. Correct the pipeline references described below and run a test deployment in a non-production workspace before enabling production.

## Pipeline setup notes

The checked-in YAML refers to repository-root paths such as `scripts/`, `pipelines/`, and `requirements.txt`, but the actual files are under `ado-pipelines/`. For example, the validation pipeline references `pipelines/templates/deploy.yml`, while the template is at `ado-pipelines/templates/deploy.yml`. Update the YAML paths (or relocate the files consistently) before running the pipeline.

The deployment template invokes `scripts/smoke_test.py`, but the checked-in script is named `scripts/smoke_tests.py`. Align the command and filename before enabling the deployment job.

## Local validation

From the repository root, install the Python dependencies and run the policy check:

```bash
python -m pip install -r ado-pipelines/requirements.txt
python ado-pipelines/scripts/validate.py
```

The policy check intentionally fails until `ado-pipelines/workspace/` contains at least one Fabric item folder and the environment replacement values in `parameter.yml` no longer contain placeholders.

To run the Python linter used by the pipeline:

```bash
python -m pip install ruff
ruff check ado-pipelines/scripts
```

## References

- [fabric-cicd documentation](https://microsoft.github.io/fabric-cicd/)
- [Introduction to Git integration in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
- [Microsoft Fabric CI/CD documentation](https://learn.microsoft.com/en-us/fabric/cicd/)
- [pre-commit](https://pre-commit.com/)

## License

This project is distributed under the [MIT License](LICENSE).
