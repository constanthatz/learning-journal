Feature: Editing



    Scenario: Find detail view at consistent url
        Given that I want to see detail for post 1
        When I enter the url /detail/1
        Then I see the content of that post

