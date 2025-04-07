from behave import given, when, then
from google.cloud import networkconnectivity_v1, compute_v1
import os
from ipaddress import IPv4Network
import time


# @given('I have a GCP project "{project_id}"')
# def step_have_gcp_project(context, project_id):
#     """Set up the GCP project for testing."""
#     # Load credentials from a service account file or environment
#     credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

#     if credentials_path and os.path.exists(credentials_path):
#         context.credentials = service_account.Credentials.from_service_account_file(
#             credentials_path
#         )
#     else:
#         # Default credentials (for local testing or when running on GCP)
#         context.credentials = None

#     context.project_id = project_id

#     # Initialize NCC clients
#     context.hub_client = networkconnectivity_v1.HubServiceClient(
#         credentials=context.credentials
#     )
#     context.spoke_client = networkconnectivity_v1.HubServiceClient(
#         credentials=context.credentials
#     )


@given('there is an NCC hub "{hub_name}" deployed within it')
def step_get_ncc_hub_from_project(context, hub_name):
    """Check the deployed NCC hub is as expected."""
    project_path = f"projects/{context.project_id}/locations/global"

    request = networkconnectivity_v1.ListHubsRequest(parent=project_path)
    response = context.hub_client.list_hubs(request=request)
    # print("RESPONSE", response)
    ncc_hubs = [hub for hub in response]
    assert (
        len(ncc_hubs) == 1
    ), f"Expected a single connectivity group, but found {len(ncc_hubs)}"
    assert (
        ncc_hubs[0].name
        == f"projects/{context.project_id}/locations/global/hubs/{hub_name}"
    ), f"Expected hub '{hub_name}', but got '{ncc_hubs[0].name}'"

    context.hub_name = hub_name


@given(
    'the "{connectivity_group}" connectivity group auto-accept list contains "{my_other_project}"'
)
def step_get_ncc_auto_accept_list(context, connectivity_group, my_other_project):
    """Check the default connectivity group auto-accepts spoke requests from target project."""

    group_name = f"projects/{context.project_id}/locations/global/hubs/{context.hub_name}/groups/{connectivity_group}"
    group_resp = context.hub_client.get_group(name=group_name)
    # print("AutoAccept Attributes2:", dir(group_resp.auto_accept.__dict__))
    assert my_other_project in str(
        group_resp.auto_accept
    ), f"Expected auto-accept list to contain '{my_other_project}', but got '{group_resp.auto_accept}'"


@when('I create a VPC network "{my_vpc_name}" in project "{my_other_project}"')
def step_create_vpc_network_in_remote_project(context, my_vpc_name, my_other_project):
    """Create a VPC Network in remote project to be attached as an NCC VPC Spoke."""

    network_client = compute_v1.NetworksClient()
    network = compute_v1.Network(name=my_vpc_name, auto_create_subnetworks=False)

    insert_vpc = network_client.insert(
        project=my_other_project, network_resource=network
    )

    context.network_client = network_client
    context.created_vpcs.append(insert_vpc)
    context.test_project_id = my_other_project

    hold = context.global_client(my_other_project, insert_vpc.name)


@when('add a subnet "{subnet_name}" to the VPC with cidr "{subnet_cidr}" in "{region}"')
def step_create_subnetwork_in_remote_project_vpc(
    context, subnet_name, subnet_cidr, region
):
    """Create a subnet within the test VPC."""

    subnet_client = compute_v1.SubnetworksClient()

    subnet = compute_v1.Subnetwork()
    subnet.name = subnet_name
    subnet.network = context.created_vpcs[0].target_link
    subnet.ip_cidr_range = subnet_cidr
    subnet.region = region

    # Create the subnet
    insert_subnet = subnet_client.insert(
        project=context.test_project_id, region=region, subnetwork_resource=subnet
    )

    subnet_hold = context.regional_client(
        context.test_project_id, insert_subnet.name, region=region
    )
    context.subnet_cidr = subnet_cidr

@when('I attach the VPC as a VPC spoke with name "{spoke_name}" to the NCC hub')
def step_create_vpc_spoke(context, spoke_name):
    """Attach the created VPC as a VPC Spoke to the local NCC hub."""
    # Take a snapshot of existing spokes of the hub
    hub_path = context.hub_client.hub_path(
        project=context.project_id,
        hub=context.hub_name,
    )

    print("uri", context.created_vpcs[0].target_link)
    spoke_name_full = f"projects/{context.test_project_id}/locations/global/spokes/{spoke_name}"

    context.hub_path = hub_path
    vpc_spoke = networkconnectivity_v1.Spoke(
        name=spoke_name_full,
        hub=context.hub_path,
        linked_vpc_network=networkconnectivity_v1.LinkedVpcNetwork(
            uri=context.created_vpcs[0].target_link
        ),
    )
    print("vpc_spoke", vpc_spoke)
    parent = f"projects/{context.test_project_id}/locations/global"

    print("hub_path", hub_path)
    print("vpc_spoke", vpc_spoke)
    request = networkconnectivity_v1.CreateSpokeRequest(
        parent=parent, spoke=vpc_spoke, spoke_id=spoke_name
    )
    print("request", request)
    create_spoke = context.hub_client.create_spoke(request=request)

    context.spoke_name = spoke_name
    # spoke_hold = context.global_client(context.test_project_id, create_spoke.name)


@then('the VPC spoke should be in an "{state}" state')
def step_ensure_active_vpc_spoke(context, state):
    """Ensure the VPC Spoke is configured as expected."""

    print("context.project_id", context.project_id)
    request = networkconnectivity_v1.GetSpokeRequest(
        name="projects/"
        + context.test_project_id
        + "/locations"
        + "/global"
        + "/spokes/"
        + context.spoke_name
    )

    response = context.spoke_client.get_spoke(request=request)
    print("response", response)

    assert (
        isinstance(response.state, type(networkconnectivity_v1.State.ACTIVE))
    ), f"Expected state '{state}', but got '{response.state}'"

@then('the NCC hub route table should contain a route for the VPC spoke')
def step_ensure_active_vpc_spoke(context):
    """Ensure the VPC Spoke propagates its subnet routes."""
    print("Sleeping for 40...")
    time.sleep(40)
    ncc_rt_name = f"projects/{context.project_id}/locations/global/hubs/{context.hub_name}/routeTables/default"
    request = networkconnectivity_v1.ListRoutesRequest(
        parent=ncc_rt_name,
    )
    result = context.hub_client.list_routes(request=request)
    print("result", result)
    new_route = [route for route in result if route.ip_cidr_range == context.subnet_cidr]
    assert (
        len(new_route) == 1
    ), f"Expected a single route for the subnet, but got {len(new_route)}"


# @then('the NCC hub should have an additional spoke')
# def step_ensure_additional_vpc_spoke(context):
#     """Ensure the VPC Spoke propagates its subnet routes."""

#     spoke_request = networkconnectivity_v1.ListSpokesRequest(parent=context.hub_path)
#     current_spokes = context.hub_client.list_spokes(parent=spoke_request)
#     current_spoke_list = [spoke for spoke in current_spokes]

#     assert len(current_spoke_list) == len(context.existing_spokes) + 1, f"Expected {len(context.existing_spokes) + 1} spokes, but got {len(current_spoke_list)}"
