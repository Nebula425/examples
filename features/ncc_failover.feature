Feature: GCP Network Connectivity Center Failover Validation
  As a cloud network engineer
  I want to verify that when I change the state of the primary network path to on-premise, the secondary then becomes the expected network path.
  So that I can ensure they comply with my network requirements

#   Scenario: Verify NCC primary failover behaviours
#     Given I have a GCP project "lab-hybrid-connectivity"
#     And there is an NCC hub "se-us-ncc-hub" deployed within it
#     And I have all VPN tunnels up in region "us-south1"
#     And I have all hybrid spokes configured in region "us-south1"
#     And I am receiving all default routes from the on-premise network from "us-south1, us-central, us-east4"
#     When I change the state of the primary network path to on-premise to "inactive"
#     Then the NCC hub route table loses 32 entries of a default route
#     And the primary network path becomes via "us-central1"