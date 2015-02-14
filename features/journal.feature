Feature: Editing



    Scenario: Find detail view at consistent url
        Given that I want to see detail for post 1
        When I enter the url /detail/1
        Then I see the detail page and the content of that post

    Scenario: Edit view
        Given that I want to edit post 1
        When I enter the url /editview/1
        Then I can see the new edit page and edit the entry

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
