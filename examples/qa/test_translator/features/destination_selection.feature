@NextDotGym
Feature: Destination Selection
  As a space traveler
  I want to browse and select destinations
  So that I can learn about potential travel locations

  Scenario: View Proxima Centauri b destination details
    Given I am on the home page
    When I navigate to the destinations section
    And I select "Proxima Centauri b" from the destinations
    Then I should see the destination name "Proxima Centauri b"
    And the mass information should be displayed
    And the temperature information should be displayed
    And the gravity information should be displayed
