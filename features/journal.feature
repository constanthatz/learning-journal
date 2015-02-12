Feature: Post Detail View
    Add a permalink to view that shows a single post

    Scenario: Find detail view at consistent url
        Given a post id
        When I enter the url /detail/id
        Then I see the detail view for the post with the given id


Feature: Editing

    Scenario: Edit view
        Given a post
        When I click a link from the detail view
        Then I am taken to the edit view

    Scenario: Edit a post
        Given that I want to edit a post
        When I alter a post in the edit view and click save
        Then the post is permanently edited in the database


Feature: Markdown

    Scenario: Add Markdown to a post
        Given that I want to add markdown to a post
        When I add markdown syntax to a post and submit
        Then markdown in the post will be rendered as properly


Feature: Code Highlighting
    Scenario: Add code blocks to a post
        Given that I want to add code blocks with highlighting to a post
        When I use backticks to denote a code block
        Then the code in that block will be colorized
