---
name: thinkidea
description: The main driving skill for human-in-the-loop agent assisted research. Given an target idea or intuition, the agent will expand the idea into detailed concepts, create new ideas, explore the idea from different perspectives, and generate new insights through an iterative process. After the ideas have been thoroughly explored, the agent will summarize the key insights and store them into the project file.
---


# ThinkIdea
ThinkIdea is a human-in-the-loop orchestration agent assisted scientific research skill. From a high level, given an target idea or intuition, you will expand the idea into detailed concepts, create new ideas, explore the idea from different perspectives, and generate new insights through an iterative process. The users will discuss with you to refine the ideas. The basic workflow is as follows:

1. Read the project documentations and understand the research topic and the current progress.
2. Understand user input in the context of the project and the current research progress.

Loop
3. Expand the idea into detailed concepts, todos, and new ideas. Use ``brainstorming-research-ideas`` and ``creative-thinking-for-research`` skills to help you with this step.
4. Conduct related work search to find relevant papers if needed. Use ``literature-search`` skill to help you with this step.
5. Whenever you think you have enough insights, ideas, or progress, communicate with the users to for discussion and feedback. Refine the ideas based on the discussion.
6. Repeat the above steps until the user is satisfied for the current round of research.

7. Summarize the key insights and store them into the project file, see Section `Project File Management` for more details.

## Project Structure

The project structure is as follows:
```
{project}/Notes/
|-- Ideas.md # Central idea tracking
|-- Plans.md # Research plans for paper writing, implementation, and todos
|-- Discussions.md # Record of discussions with users
|-- Literature/ # Folder for storing literature review notes
    └── Literature.md # File for summarizing and tracking literature review
```

Under [templates/](templates/) directory, you can find templates for the above markdown files, along with the description of what each file is for and how to use it. If `{project}/Notes/` directory or any of the above files do not exist, you should create them based on the templates and fill in the initial information based on the project documentation.


## Literature Management

When you find relevant papers during the research process, you should create a new markdown file under `{project}/Notes/Literature/` to summarize the paper. The file name should be the title of the paper. The content of the file should include the following sections: