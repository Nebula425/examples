Feature: GCP Network Connectivity Center VPC Spoke Validation
  As a cloud network engineer
  I want to verify that when I attach a VPC to an NCC hub as a VPC Spoke, the VPC Spoke exhibits the correct behaviours
  So that I can ensure they comply with my network requirements

  Scenario: Verify VPC Spoke behaviours
    Given I have a GCP project "<>"
    And there is an NCC hub "<>" deployed within it
    And the "default" connectivity group auto-accept list contains "<>"
    When I create a VPC network "my-vpc-spoke-test" in project "<>"
    And add a subnet "my-vpc-spoke-subnet" to the VPC with cidr "10.0.4.0/24" in "us-south1"
    And I attach the VPC as a VPC spoke with name "my-test-vpc-spoke" to the NCC hub

    Then the VPC spoke should be in an "ACTIVE" state
    And the NCC hub route table should contain a route for the VPC spoke