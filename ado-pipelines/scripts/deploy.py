"""Deploy Fabric item definitions from the repo to a workspace using fabric-cicd.

"""
import argparse

from azure.identity import AzureCliCredential
from fabric_cicd import (
    FabricWorkspace,
    change_log_level,
    publish_all_items,
    unpublish_all_orphan_items,
)

#These are items types that are used in workspace in fabric. There are more, but these are most basic ones
# and are supported by fbric-cicd api docs.
DEFAULT_ITEM_TYPES = ["Notebook", "DataPipeline", "Environment", "VariableLibrary"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace-id", required=True)
    p.add_argument("--environment", required=True, help="Key in parameter.yml, e.g. TEST or PROD")
    p.add_argument("--repo-dir", default="workspace")
    p.add_argument("--item-types", nargs="*", default=DEFAULT_ITEM_TYPES)
    p.add_argument("--unpublish-orphans", action="store_true",
                   help="Delete items in the workspace that are not in the repo")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    if args.debug:
        change_log_level("DEBUG")

    target = FabricWorkspace(
        workspace_id=args.workspace_id,
        environment=args.environment,
        repository_directory=args.repo_dir,
        item_type_in_scope=args.item_types,
        token_credential=AzureCliCredential(),
    )

    publish_all_items(target)
    if args.unpublish_orphans:
        unpublish_all_orphan_items(target)


if __name__ == "__main__":
    main()