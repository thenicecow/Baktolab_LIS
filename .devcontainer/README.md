This devcontainer provides a development environment for the Baktolab_LIS project.

To open the project in the container from VS Code: choose **Remote-Containers: Reopen in Container**.

To build the container from the command line (requires `devcontainer` CLI):

```bash
devcontainer build --workspace-folder .
devcontainer up --workspace-folder .
```

The container will run `pip install -r requirements.txt` automatically after creation if the file exists.
