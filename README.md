# StarCMS
![image](https://github.com/user-attachments/assets/c523dfe1-901e-4e8a-85bf-214a37c0438d)

StarCMS is a powerful CMS designed with simplicity in mind. It is ideal for bloggers, novel writers, and other various end-users as it is designed to be extremely simple yet with power features.

## Features
- Automatic Hierachy | Designed like a file system, StarCMS allows for highly complex storage of data.
- Background Management | Simple backgrounds design for bucket, spreading it to all its pages for consistency and beauty.
- User Systems | Collaborate with ease across several authors through internal web, maximizing security. 
- Administration | Easy to use frontend to change the background.

## Purpose
This project's use case is for creating and managing any document that severely relies on paging while providing a streamlined workflow for publishing to the web.
This particularly exists for the two following purposes:
- Webnovels
- Blogs

### What current software exist for such?
- Github Gists
- Wordpress
- Medium
- Blog post pages
- OneNote
- Obsidian
- Word/Docs

### Benefits compared to...
Gists
- Significantly more powerful editor
- Bucket filesystem for complex hierarchies of blogs

Medium
- Bucket filesystem for complex hierarchies of blogs

Wordpress
- Significantly more powerful editor
- Built-in rails for hierachy intead of manual

Onenote/Obsidian
- Contains streamlined pipe to web
- Complex multi-tier "notebooks" instead of just 1

Word/Docs
- Most do not think of each page as an individual document, and lack features for pages (e.g, word count per page)
- Clunky export integration pipeline (no CI/CD to publish to web)
- Peformance issues on those with individual pages. (not good for >300 pages)

## Current Status
Currently in beta. Public endpoint is secured, however, private endpoint is very unsecure for the following reasons. [Details can be found here.](https://github.com/mzen17/StarCMS/wiki/Listed-Vulnerabilities)

Other problems
- Many skeletons in the API.
- Documententation of code subpar.

Production-ready deployment is doable, however, it is important to keep private endpoint inside an internal network that has no public access, where you know all the entities using it.

## Usage Notes
Create a venv, install reqs.txt. Create a .env file, and place tinymce url into it. Input S3 credentials for image support.
Then, create a sqlite3 database in the directory called app.db. and run the following command to bring up the webserver:\

```./run.sh```\
```./prun.sh```

The first runs the viewer, the second runs the editor.

Navigate to the URL. It does not have a functional GUI to create users, so go to the URL/docs, and use the "Try It" button in the FastAPI docs. The app is now ready, but do note that to delete pages, buckets, or users, you must use SQL and execute it on the app.db.

## Toolchain and framework
All new projects must have their toolchain and framework defined before the project starts.

If new tools need to be added during project, they must have a good reason.

- Python with FastAPI.
- Database with SQLite/PostgreSQL
- TinyMCE for frontend editing.
- Raw HTML on frontend
