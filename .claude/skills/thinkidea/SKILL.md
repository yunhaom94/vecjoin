---
name: thinkidea
description: The main driving skill for human-in-the-loop agent assisted research. Given an target idea or intuition, the agent will expand the idea into detailed concepts, create new ideas, explore the idea from different perspectives, and generate new insights through an iterative process. After the ideas have been thoroughly explored, the agent will summarize the key insights and store them into the project file. This skill is invoked when the user specifies an topic, idea or intuition and ask for help to explore, brainstorm, or work on the idea.
---


# ThinkIdea
ThinkIdea is a human-in-the-loop orchestration agent assisted scientific research skill. From a high level, given an target idea or intuition, you will use the given background under `{project}/Notes/` and expand the idea into detailed concepts, design and implementation details, create new ideas, explore the idea from different perspectives, and generate new insights through an iterative process. The users will constantly discuss with you to refine the ideas. The overarching goal is to iterativly build a concrete design under the 'Main Ideas' section in `{project}/Notes/Ideas.md`.

Before you start the workflow, you should first identify the stages of this research process by reading the project documentation. 

## Workflow Overview

1. Read the project documentations and understand the research topic and the current progress.
2. Understand user input in the context of the project and the current research progress.
3. Expand the idea into detailed concepts, todos, and new ideas. Use ``brainstorming-research-ideas`` and ``creative-thinking-for-research`` skills if needed to help you with this step.
4. Conduct related work search to find relevant papers if needed or asked. Use ``literature-search`` skill to help you with this step.
5. Go to 3 and repeat, until the user is satisfied for the current round of research.
6. Summarize the key insights and store them into the project file, see Section `Project File Management` for more details.

## Project Structure

The project structure is as follows:
```
{project}/Notes/
|-- Ideas.md # Central idea tracking
|-- Plans.md # Research plans for paper writing, implementation, and todos
|-- Literatures/ # Folder for storing PDFs and literature tracking
    └── Literatures.md # File for summarizing and tracking literature review
```

Under [templates/](templates/) directory, you can find templates for the above markdown files, along with the description of what each file is for and how to use it. If `{project}/Notes/` directory or any of the above files do not exist, you should create them based on the templates and fill in the initial information based on the project documentation.

## Step 1: Understand the Project and Research Progress

Use `Ideas.md` and `Plans.md` to understand the current research progress and the background of the project. You can also read any other files under `Notes/` to get more information about the project. If there are any code files, you can also read them to understand the implementation details.

## Step 2: Understand User Input

You should use the project background and the current research progress to understand the user input. The first thing you should do is to ask the user to clarify the idea or intuition they want to explore, and make sure you understand it correctly. Ask user to clarify the idea if it is not clear to you. You can also ask user to provide more information about the idea if needed, such as the motivation behind it, the potential impact, and any related work they are aware of.

## Step 3: Expand the Idea

After you have a clear understanding of the idea, you should expand it into detailed concepts, implementation details, create new ideas, explore the idea from different perspectives, and generate new insights through an iterative process. All of the above may occur at the same time, or in any order. 

You can use `brainstorming-research-ideas` and `creative-thinking-for-research` skills to help you with this step. You should also communicate with the user to get their feedback and refine the ideas based on the discussion.

## Step 4: Related Work Search

If the knowledge gap is related to understanding the current state of the art, after a few rounds of discussion for grounding, or prompted by users, you should conduct related work search to find relevant papers, invoke the `literature-search` skill as a sub-agent using the Agent tool. Provide it with:
- The **topic summary** (from Ideas.md or the current discussion)
- The **problem statement** (the specific research question being explored)

The literature-search skill will autonomously search Semantic Scholar, arXiv, and Google Scholar, filter candidates by relevance, download papers and convert them to Markdown (via markitdown) under `{project}/Notes/Literatures/`, and append structured summaries to `{project}/Notes/Literatures/Literatures.md`.

Example invocation:
```
Use the Agent tool with the literature-search skill:
  "Search for related work on the following topic:
   Topic: {summary of the research topic}
   Problem: {the specific problem or question}
   Project root: {project root path}"
```

After the literature-search agent completes, review its results and discuss with the user
which papers are most relevant and how they inform the research direction. Based on user feedback, update the record in `{project}/Notes/Literatures/Literatures.md`, removing less relevant papers and adding any additional notes or insights from the discussion. 

## Step 5: Iterate
Unless user is satisfied with the current research progress, you should go back to Step 3 and repeat the process. 

## Step 6: Summarize Key Insights and Store in Project File
After the user is satisfied with the current research progress, you should summarize the key insights and store them into the project file. Use `Plans.md` to record the research plans for paper writing, implementation, and todos. Use `Ideas.md` to record the central ideas and concepts - see the file for detailed categorizations. Make sure to update the files in a clear and organized way, use hierarchical structure, bullet points, and formatting to make the information easy to read and understand. 

**Important** it is very likely that an idea is already mentioned in the project file, if that is the case, you should not create a new record for it, but instead update the existing record with new information, or with sub points if it is a main idea. 

**Important** At the end of a discussion session, you should condense any intermediate insights in the notes, and reorganize the notes as needed to make it more clear and organized. 
## Important Notes
- Always keep the user in the loop and make sure to communicate with them regularly to get their feedback and refine the ideas based on the discussion. For discussion, always use a numbered list for the points you want to discuss, and ask the user to respond with the number of the point they want to discuss. 

- Users may update the notes files manually, or ask you to note something during a discussion session. Always treat the content in the files as the most up-to-date information about the project, and make sure to read them before making any decisions or suggestions.

- Important: DO NOT change the organization or description of the points that is outside the scope of the user specified task!!! If you find there are other points that are related and you want to merge or reorganize them, always ask the user.

- The levels of details in the ideas file vary greatly, from high-level concepts to detailed implementation details. You should use your judgment to decide how much detail to include in each idea, and how to organize the ideas in a clear and logical way.

- The workflow is not strictly linear, you can go back and forth between different steps as needed. For example, you may need to go back to Step 1 to read more about the project background, or go back to Step 3 to refine the ideas based on user feedback. User may also ask you to read specific papers.

- When doing foundational research, you should invoke literature search more frequently to get more information about the current state of the art, and to get more insights from the related work. When doing incremental research, you may not need to do literature search as frequently, but you should still keep an eye on the related work to make sure your research is novel and relevant.