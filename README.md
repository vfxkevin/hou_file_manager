# Houdini File Path Manager
A GUI tool and central place for managing all Houdini file paths of node parameters.

## Installation
* Download the source code zip file.
* Unzip it to a location.
  * Say, it is D:/my_hou_pkg/hou_file_manager
    * NOTE: This is a Windows path example, your actual path could be different.
* Move the hou_file_manager.json file into the 'packages' directory inside the **Houdini user preference directory** ($HOUDINI_USER_PREF_DIR).
  * On Windows, the **Houdini user preference directory** is C:/Users/_**username**_/Documents/houdini20.5 (for Houdini 20.5)
    * NOTE: Replace the _**username**_ with the actual name on your computer for the actual path.
  * Create a 'packages' directory inside the **Houdini user preference directory** if there is none.
* Modify the hou_file_manager.json file, so that the HOU_FILE_MANAGER env variable points to the above unzipped directory.
  * In our example, it would be like:
    ```
          "env": [
          {
              "HOU_FILE_MANAGER": "D:/my_hou_pkg/hou_file_manager"
          }
      ]
    ```
* Re-launch Houdini.
* The Hou File Manager GUI can be found when creating a New Pane Tab.
