# Houdini File Path Manager
A GUI tool and central place for managing all Houdini file paths of node parameters.

## Installation
* Go to [Releases](https://github.com/vfxkevin/hou_file_manager/releases) and download the **source code zip file** from the latest release.
  * For example, release `v0.1.0` is downloaded.
* Unzip it to a location.
  * In our example, it is `D:/<path_to>/hou_file_manager-0.1.0`
  * NOTE:
    * This is a Windows path example, `<path_to>` could be different based on your preference.
    * The actual package directory path is `D:/<path_to>/hou_file_manager-0.1.0/hou_file_manager-0.1.0` (the double hou_file_manager-0.1.0) because the way it was zipped.
* Move the `hou_file_manager.json` file into the `packages` directory inside the `Houdini user preference directory` ($HOUDINI_USER_PREF_DIR).
  * On Windows, the `Houdini user preference directory` is `C:/Users/<username>/Documents/houdini20.5` (for Houdini 20.5)
    * NOTE: Replace the `<username>` with the actual name on your computer for the actual path.
  * Create a `packages` directory inside the `Houdini user preference directory` if there is none.
* Modify the `hou_file_manager.json` file, so that the `HOU_FILE_MANAGER` env variable points to the above unzipped directory.
  * In our example, it would be like:
    ```
          "env": [
          {
              "HOU_FILE_MANAGER": "D:/my_hou_pkg/hou_file_manager-0.1.0/hou_file_manager-0.1.0"
          }
      ]
    ```
  * Please use back slashes in the path string. 
* Re-launch Houdini.
* The Hou File Manager GUI can be found when creating a New Pane Tab.
