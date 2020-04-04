Feature:
  @createStudent
  Scenario Outline: Deleting student End to End scenario

    Given user deletes student with "<resource>"
    And user goes to cybertek training application
    Then user searches for student with student ID "<studentID>"
    And user verifies that no result should show

    Examples:
      | resource             | studentID |
      | /student/delete/7651 | 7651      |