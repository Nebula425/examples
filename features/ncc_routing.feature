Feature: GCP Network Connectivity Center Routing
  As a cloud network engineer
  I want to verify deployed NCC resources have the correct behaviours when it comes to primary, secondary and tertiary Routing

  Scenario: Verify basic routing properties for NCC hub
    Given I have a GCP project "<>"
    When I get the route table for NCC hub "<>"
    Then the NCC hub route table should be the "default" route table
    And the NCC hub route table should have 3 active routes
    And the NCC hub route table does not contain any "240.0.0.0/4" routes

#   Scenario: Verify hierarchical routing properties for NCC hub
#     Given I have a GCP project "lab-hybrid-connectivity"
#     When I get the route table for NCC hub "se-us-ncc-hub"
    # Then the NCC route table for us-east4 should have a primary route region of "us-east4"
    # And NCC route table for us-east4 should have a secondary route region of "us-central1"
    # And NCC route table for us-east4 should have a tertiary route region of "us-south1"

# Repeat for the other two regions.