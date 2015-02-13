Feature: Editing



    Scenario: Find detail view at consistent url
        Given that I want to see detail for post 1
        When I enter the url /detail/1
        Then I see the detail view for post 1


    Scenario: Edit view
        Given a post
        When I click a link from the detail view
        Then I am taken to the edit view

    Scenario: Edit a post
        Given that I want to edit a post
        When I alter a post in the edit view and click save
        Then the post is permanently edited in the database


    Scenario: Add Markdown to a post
        Given that I want to add markdown to a post
        When I add markdown syntax to a post and submit
        Then markdown in the post will be rendered as properly

    Scenario: Add code blocks to a post
        Given that I want to add code blocks with highlighting to a post
        When I use backticks to denote a code block
        Then the code in that block will be colorized
