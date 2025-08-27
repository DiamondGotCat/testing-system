# AutoTestingSystem
A repository that automatically tests multiple software programs and generates log files.

## Before you begin

<img width="480" height="270" alt="Screenshot from 2025-08-27 14-27-05" src="https://github.com/user-attachments/assets/d5bbf70e-4d1b-4d94-a8f1-04cde9606340" />

### 1. Copying this Template Repository
Create a new repository based on this template repository.

### 2. Give the runner write permissions
In your GitHub repository's "Actions" settings, go to the "General" page and set the permissions to "Read and write permissions."
This will allow the system to automatically generate log files, etc.

## How to Customize
Customization typically involves modifying only the following files/directories:
- `tests` directory
- `config.json` file
Place a test Python script in the `tests` directory and modify config.json to include the new Python script.
You can also change the schedule by changing the `- cron: "0 0,6,12,18 * * *"` part in `.github/workflows/main.yml`.

## Enable Actions
To start working, rename `.github.disabled` to `.github`.
Note that this will not work in environments where Github Actions is not running.
