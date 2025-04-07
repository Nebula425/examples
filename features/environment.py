# environment.py
from google.cloud import compute_v1
from google.cloud import networkconnectivity_v1


import os

# def before_all(context):
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/jameskelly/Downloads/lab-tenant-7527b5e24091.json"


# def delete_vpc(project_id, vpc_name):
#     """
#     Delete a VPC network and all its subnets.

#     Args:
#         project_id (str): Google Cloud project ID
#         vpc_name (str): Name of the VPC to delete
#     """
#     # Initialize clients
#     network_client = compute_v1.NetworksClient()

#     try:
#         # Need to get all subnets first
#         subnet_client = compute_v1.SubnetworksClient()

#         # List all subnets for this network - need to check all regions
#         region_client = compute_v1.RegionsClient()
#         regions_list = region_client.list(project=project_id)

#         # Collect subnet deletion operations to track
#         subnet_operations = []

#         # Delete all subnets in each region
#         for region in regions_list:
#             try:
#                 subnets = subnet_client.list(project=project_id, region=region.name)

#                 # Find subnets that belong to this network
#                 for subnet in subnets:
#                     if vpc_name in subnet.network:
#                         print(f"Deleting subnet {subnet.name} in {region.name}")
#                         operation = subnet_client.delete(
#                             project=project_id,
#                             region=region.name,
#                             subnetwork=subnet.name,
#                         )
#                         subnet_operations.append((region.name, operation.name))
#             except Exception as e:
#                 print(f"Error listing subnets in region {region.name}: {e}")

#         # Wait for all subnet deletions to complete
#         region_operation_client = compute_v1.RegionOperationsClient()
#         for region_name, operation_name in subnet_operations:
#             region_operation_client.wait(
#                 project=project_id, region=region_name, operation=operation_name
#             )

#         # Now delete the network
#         print(f"Deleting VPC network {vpc_name}")
#         operation = network_client.delete(project=project_id, network=vpc_name)

#         # Wait for the operation to complete
#         operation_client = compute_v1.GlobalOperationsClient()
#         operation_client.wait(project=project_id, operation=operation.name)
#         print(f"Successfully deleted VPC {vpc_name}")
#         return True

#     except NotFound:
#         print(f"VPC {vpc_name} not found, possibly already deleted")
#         return True
#     except Exception as e:
#         print(f"Error deleting VPC {vpc_name}: {e}")
#         return False


# def after_scenario(context, scenario):
#     """Clean up resources after each scenario."""
#     # Check if we have any VPCs to clean up
#     if hasattr(context, "created_vpcs") and context.created_vpcs:
#         print(f"Cleaning up {len(context.created_vpcs)} VPCs...")

#         # context.created_vpcs should be a list of (project_id, vpc_name) tuples
#         for project_id, vpc_name in context.created_vpcs:
#             delete_vpc(project_id, vpc_name)

#         # Clear the list after cleanup
#         context.created_vpcs = []


# Optional: Initialize the created_vpcs list in before_all
def before_all(context):
    """Set up environment before all scenarios."""

    # Initialize a list to store created VPCs
    def ops_glob_client(project: None, operation: None):
        operation_client = compute_v1.GlobalOperationsClient()
        operation_client.wait(project=project, operation=operation)
        return operation_client

    def ops_reg_client(project: None, operation: None, region: None):
        operation_client = compute_v1.RegionOperationsClient()
        operation_client.wait(project=project, operation=operation, region=region)
        return operation_client

    context.created_vpcs = []
    context.global_client = ops_glob_client
    context.regional_client = ops_reg_client


# def _delete_vpc_spoke(context):
#     request = networkconnectivity_v1.DeleteSpokeRequest(name="projects/lab-tenant/locations/global/spokes/my-test-vpc-spoke")
#     operation = context.hub_client.delete_spoke(request=request)
#     response = operation.result()
#     return response


# def _delete_vpc_network(context):
#     pass


# def after_all(context):
#     """Delete resources created during testing."""

#     vpc_response = _delete_vpc_spoke(context)
#     print(vpc_response)
