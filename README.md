# Project
Page Word Processor is a web-based word processor with a very niche use case.

## Why?
As per new guidelines for my projects in 2024 all project must provide ample 
reason for existence.

This project's use case is for creating and managing any document that severely relies on paging.
This includes things such as

- Notes
- Web Novel pages
- Blog post pages

What current software exist for such?

- OneNote
- Obsidian
- Word/Docs

Why not use one of the above instead of creating?

- Most do not think of each page as an individual document.
- Peformance issues on those with individual pages.
- Propertiary Software that requires either WiFi, or payment.

Pre-defined limitations (Before Implementation)
- Useless for anything that is "pageless" in a sense, where pages don't mean anything.


## Current Status
MVP state. Do not use in production unless in a private network with a firewall.

Very unsecure.

- Createusers endpoint can be spammed to flood database and prevent normal users
- Pages may be returned to people who don't own them by modifying front end.
- Bucket and page endpoints can be flooded to waste storage

Other problems

- GUI is not in any good shape.
- DELETE buttons are not implemented, nor is the DELETE API functional.
- Many skeletons in the API.
- Documententation of code subpar. 
- Code has many illogically structured APIs, and needs plenty of refactoring.

## Toolchain and framework
All new projects must have their toolchain and framework defined before the project starts.

If new tools need to be added during project, they must have a good reason.

- Python with FastAPI.
- Database with SQLite/PostgreSQL
- TinyMCE for frontend editing.
- HTMX (if needed), or a mightier frontend (React, Svelte)