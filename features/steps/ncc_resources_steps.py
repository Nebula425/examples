from behave import given, when, then
from google.cloud import networkconnectivity_v1
import os
from google.oauth2 import service_account


@given('I have a GCP project "{project_id}"')
def step_have_gcp_project(context, project_id):
    """Set up the GCP project for testing."""
    # Load credentials from a service account file or environment
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if credentials_path and os.path.exists(credentials_path):
        context.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
    else:
        # Default credentials (what is signed in with gcloud)
        context.credentials = None

    context.project_id = project_id

    # Initialize NCC clients
    context.hub_client = networkconnectivity_v1.HubServiceClient(
        credentials=context.credentials
    )
    context.spoke_client = networkconnectivity_v1.HubServiceClient(
        credentials=context.credentials
    )


@when('I get the NCC hub "{hub_name}"')
def step_get_ncc_hub(context, hub_name):
    """Retrieve a Network Connectivity Center hub from GCP."""
    hub_path = context.hub_client.hub_path(
        project=context.project_id,
        hub=hub_name,
        # location="global"
    )
    context.hub = context.hub_client.get_hub(name=hub_path)
    context.hub_name = hub_name


@then('the NCC hub should have description "{description}"')
def step_check_hub_description(context, description):
    """Verify the NCC hub has the expected description."""
    assert (
        context.hub.description == description
    ), f"Expected hub description '{description}', but got '{context.hub.description}'"


# @then('the NCC hub should be in topology mode "{topology_mode}"')
# def step_check_hub_topology(context, topology_mode):
#     """Verify the NCC hub has the expected topology configuration."""
#     print(str(context.hub.preset_topology))
#     assert context.hub.preset_topology == topology_mode, \
#         f"Expected topology type of {topology_mode}, but got {context.hub.preset_topology}"


@then("the NCC hub should have a single connectivity group {connectivity_group}")
def step_check_hub_connectivity_group(context, connectivity_group):
    """Verify the NCC hub has only the default connectivity group."""
    parent = context.hub_client.hub_path(
        project=context.project_id,
        hub=context.hub_name,
    )
    request = networkconnectivity_v1.ListGroupsRequest(parent=parent)
    conn_groups = context.hub_client.list_groups(request=request)
    conn_group_list = [group for group in conn_groups]
    assert (
        len(conn_group_list) == 1
    ), f"Expected a single connectivity group, but found {len(conn_group_list)}"
    assert (
        conn_group_list[0].name == parent + "/groups/default"
    ), f"Expected the default connectivity group, but got {conn_group_list[0].name}"


# @then('the NCC hub should have labels with "{label_pair}"')
# def step_check_hub_labels(context, label_pair):
#     """Verify the NCC hub has the expected label."""
#     key, value = label_pair.split(':')
#     labels = context.hub.labels or {}

#     assert key in labels, f"Label key '{key}' not found in hub labels"
#     assert labels[key] == value, \
#         f"Expected label value '{value}' for key '{key}', but got '{labels[key]}'"


@then("the NCC hub should have at least {count:d} spokes")
def step_check_hub_spoke_count(context, count):
    """Verify the NCC hub has at least the expected number of spokes."""
    parent = context.hub_client.hub_path(
        project=context.project_id,
        hub=context.hub_name,
    )
    request = networkconnectivity_v1.ListHubSpokesRequest(name=parent)
    spokes = context.hub_client.list_hub_spokes(request=request)
    spoke_list = [spoke for spoke in spokes]
    assert (
        len(spoke_list) >= count
    ), f"Expected at least {count} spokes, but found {len(spokes)}"


# @when('I get the NCC spoke "{spoke_name}" in hub "{hub_name}"')
# def step_get_ncc_spoke(context, spoke_name, hub_name):
#     """Retrieve a NCC spoke from GCP."""
#     # We don't know the region yet, so we need to list all spokes and find the one we want
#     hub_path = context.hub_client.hub_path(
#         project=context.project_id,
#         hub=hub_name,
#         # location="global"
#     )

#     # List all spokes in the hub
#     spokes = list(context.spoke_client.list_spokes(parent=hub_path))

#     # Find the spoke with the matching name
#     for spoke in spokes:
#         if spoke.name.split('/')[-1] == spoke_name:
#             context.spoke = spoke
#             return

#     assert False, f"Spoke '{spoke_name}' not found in hub '{hub_name}'"

# @then('the spoke should have type "{spoke_type}"')
# def step_check_spoke_type(context, spoke_type):
#     """Verify the NCC spoke has the expected type."""
#     # Get the enum value's name from the spoke type
#     actual_type = networkconnectivity_v1.Spoke.Type(context.spoke.type).name

#     assert actual_type == spoke_type, \
#         f"Expected spoke type '{spoke_type}', but got '{actual_type}'"

# @then('the spoke should be in region "{region}"')
# def step_check_spoke_region(context, region):
#     """Verify the NCC spoke is in the expected region."""
#     # Extract the region from the spoke's name (format: projects/*/locations/REGION/hubs/*/spokes/*)
#     name_parts = context.spoke.name.split('/')
#     location_index = name_parts.index('locations') + 1
#     actual_region = name_parts[location_index] if location_index < len(name_parts) else None

#     assert actual_region == region, \
#         f"Expected spoke to be in region '{region}', but it's in '{actual_region}'"

# @then('the spoke should have linked resource containing "{resource_substring}"')
# def step_check_spoke_linked_resource(context, resource_substring):
#     """Verify the NCC spoke has a linked resource containing the expected substring."""
#     linked_resources = context.spoke.linked_vpn_tunnels or context.spoke.linked_interconnect_attachments or \
#                        context.spoke.linked_router_appliance_instances or []

#     if not linked_resources:
#         assert False, "Spoke has no linked resources"

#     for resource in linked_resources:
#         if resource_substring in resource.uri:
#             return

#     assert False, f"No linked resource containing '{resource_substring}' found"

# @then('the spoke should have state "{state}"')
# def step_check_spoke_state(context, state):
#     """Verify the NCC spoke has the expected state."""
#     # Get the enum value's name from the spoke state
#     actual_state = networkconnectivity_v1.Spoke.State(context.spoke.state).name

#     assert actual_state == state, \
#         f"Expected spoke state '{state}', but got '{actual_state}'"
