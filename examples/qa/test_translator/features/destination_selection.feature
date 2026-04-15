@NextDotGym
Feature: Destination Selection
  As a space traveler
  I want to browse and select destinations
  So that I can learn about potential travel locations

  Background:
    Given I am on the home page
    When I navigate to the destinations section
    And I select "Proxima Centauri b" from the destinations

  Scenario: View destination details
    Then I should see the destination name "Proxima Centauri b"
    And the mass information should be displayed
    And the temperature information should be displayed
    And the gravity information should be displayed

  Scenario: Extract and verify destination name
    When I extract the destination name and store it as "destination_name"
    Then I should see the destination name matches "${destination_name}"

  Scenario: Calculate travel cost using custom function
    When I extract the destination name and store it as "destination_name"
    And I extract the mass as a string and store it as "mass_info"
    And I call 'format_destination_info' with destination_name "${destination_name}" and mass "${mass_info}" and store as 'formatted_info'
    And I call 'calculate_travel_cost' with base_price 1000 and distance_multiplier 4.2 and store as 'total_cost'
    Then the mass information should be displayed