Feature: GCP Network Connectivity Center Validation
  As a cloud network engineer
  I want to verify deployed NCC resources have the correct attributes
  So that I can ensure they comply with my network requirements

  Scenario: Verify NCC hub attributes
    Given I have a GCP project "lab-hybrid-connectivity"
    When I get the NCC hub "se-us-ncc-hub"
    Then the NCC hub should have description "NCC Hub for US geography."
    And the NCC hub should have a single connectivity group "default"
    # And the NCC hub should be in topology mode "PresetTopology.MESH"
    And the NCC hub should have at least 1 spokes

#   Scenario: Verify NCC spoke attributes
#     Given I have a GCP project "lab-dns-451411"
#     When I get the NCC spoke "vpn-spoke" in hub "se-us-ncc-hub"
#     Then the spoke should have type "VPN_TUNNEL"
#     And the spoke should be in region "us-central1"
#     And the spoke should have linked resource containing "vpn-tunnel"
#     And the spoke should have state "ACTIVE"