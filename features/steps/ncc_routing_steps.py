from behave import given, when, then
from google.cloud import networkconnectivity_v1
import os
from ipaddress import IPv4Network


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


@when('I get the route table for NCC hub "{hub_name}"')
def step_get_ncc_hub_route_table(context, hub_name):
    """Retrieve route table information relating to the specified NCC hub."""
    hub_path = context.hub_client.hub_path(
        project=context.project_id,
        hub=hub_name,
    )
    context.hub_name = hub_name
    context.hub_path = hub_path

    request = networkconnectivity_v1.ListRouteTablesRequest(parent=hub_path)
    response = context.hub_client.list_route_tables(request=request)
    context.ncc_route_table = response


@then('the NCC hub route table should be the "{default}" route table')
def step_check_ncc_route_table_is_default(context, default):
    """Check the default route table is the one used by the NCC hub."""

    expected_rt_name = f"projects/{context.project_id}/locations/global/hubs/{context.hub_name}/routeTables/default"
    context.ncc_rt_name = expected_rt_name
    route_tables = [rt for rt in context.ncc_route_table]
    assert (
        len(route_tables) == 1
    ), f"Expected a single route table, but got {len(route_tables)}"
    assert (
        route_tables[0].name == expected_rt_name
    ), f"Expected default route table '{expected_rt_name}', but got '{route_tables[0].name}'"


@then("the NCC hub route table should have {count:d} active routes")
def step_check_ncc_route_table_has_expected_routes(context, count):
    """Check the default NCC route table has the expected number of active routes."""

    request = networkconnectivity_v1.ListRoutesRequest(
        parent=context.ncc_rt_name,
    )
    result = context.hub_client.list_routes(request=request)

    routes = [
        route
        for route in result
        if isinstance(route.state, type(networkconnectivity_v1.State.ACTIVE))
    ]
    assert len(routes) == count, f"Expected {count} routes, but got {len(routes)}"

    context.ncc_active_routes = routes


@then('the NCC hub route table does not contain any "{class_e_range}" routes')
def step_check_ncc_route_table_has_no_class_e(context, class_e_range):
    """Check the default NCC route table does not contain any class E ranges."""
    for route in context.ncc_active_routes:
        assert not IPv4Network(route.ip_cidr_range).subnet_of(
            IPv4Network(class_e_range)
        ), f"Route {route.name} contains class E range {range}"
