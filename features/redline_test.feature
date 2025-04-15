Feature: GCP Network Connectivity Center Redline Example
  As a cloud network engineer
  I want to verify that as a VPC Spoke, I am not able to access the internet or public IPs.
  So that I can ensure they comply with my network requirements

#   Scenario: Verify VPC Spoke behaviours
#     Given I have a GCP project "lab-hybrid-connectivity"
#     And there is an NCC hub "se-us-ncc-hub" deployed within it
#     And the "default" connectivity group auto-accept list contains "lab-tenant"
#     When I create a VPC network "my-vpc-spoke-test" in project "lab-tenant"
#     And add a subnet "my-vpc-spoke-subnet" to the VPC with cidr "10.0.4.0/24" in "us-south1"
#     And I attach the VPC as a VPC spoke with name "my-test-vpc-spoke" to the NCC hub

#     Then the VPC spoke should be in an "ACTIVE" state
#     And the NCC hub route table should contain a route for the VPC spoke
#     # And the NCC hub should have an additional spoke