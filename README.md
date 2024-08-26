# Houdini File Path Manager
A GUI tool and central place for managing all Houdini file paths (textures, images, caches, geometries) of node parameters.
![hou_file_manager_gui_01](https://github.com/user-attachments/assets/72080231-e58c-43fc-b32f-6c56a8f03f2f)

## Functionalities:
* Refresh button for refreshing the Node View when Houdini scene is changed.
  * Node View selection will be cleared once Refresh button is clicked.
  * Parameter View will be cleared as well.
* Search in a path for nodes with file parmaters (image or geometry).
  * Multiple search filters are supported:
    * Node Name: Houdini multi name patterns, like *, ^ and combinations.
      * For example,
        * `*` for any names.
        * `pri*` for any names start with `pri`.
        * `* ^pri*` for any names NOT start with `pri`.
        * `*tmp` for any names end with `tmp`.
        * `* ^*tmp` for any names NOT end with `tmp`.
        * `pri* ^*tmp` for any names start with `pri` but NOT end with `tmp`.
        * `*shader*` for any names with `shader` in it.
  * Node Type: Houdini single name patterns.
  * Parameter Name: Houdini multi name patterns, like *, ^ and combinations.
    * Refer to above Node Name multi name patterns.
  * Parameter File Type: Image or Geometry.
* Node View
  * It only shows the nodes based on the search results.
  * The nodes with file parametes will be highlighted with red color.
  * Double click on a node will set current selected node to it in the Network Editor.
* Parameter View
  * The file parmaeters will be shown in the Parameter View for the selected nodes in the Node View
    * Not the actual selected nodes in Network Editor.
  * Each file parameter item in the Parameter View has:
    * A 'File Choose' button to choose a file for it, and
    * A 'Preview' button to preview the image in MPlay minimal mode.
  * The Raw Value of the file parameter in the Parameter View can be edited in place by double-clicking on it.
* Tools UI
  * Files in the Parameter View can be copied or moved to a desination diretory, and the raw value file paths of the parmaeters will be updated to the new paths.
  * <UDIM> files are supported.
  * $F or ${F} seqeuence files are supported. $F can have zero paddings, such as $F4 etc.

## Installation
* Go to [Releases](https://github.com/vfxkevin/hou_file_manager/releases) and download the **source code zip file** from the latest release.
  * For example, release `v0.1.1` is downloaded.
* Unzip it to a location.
  * In our example, say, it is `C:/Users/username/Documents/hou_file_manager-0.1.1`
  * NOTE:
    * This is a Windows path example. Please replace `username` with your actual user name.
    * The actual package directory path is `C:/Users/username/Documents/hou_file_manager-0.1.1/hou_file_manager-0.1.1` (the double hou_file_manager-0.1.1) because the way it was zipped.
* Move the `hou_file_manager.json` file into the `packages` directory inside the `Houdini user preference directory` ($HOUDINI_USER_PREF_DIR).
  * On Windows, the `Houdini user preference directory` is `C:/Users/username/Documents/houdini20.5` (for Houdini 20.5)
    * NOTE: Replace the `username` with the actual name on your computer for the actual path.
  * Create a `packages` directory inside the `Houdini user preference directory` if there is none.
* Modify the `hou_file_manager.json` file, so that the `HOU_FILE_MANAGER` env variable points to the above unzipped directory.
  * In our example, it would be like:
    ```
          "env": [
          {
              "HOU_FILE_MANAGER": "C:/Users/username/Documents/hou_file_manager-0.1.1/hou_file_manager-0.1.1"
          }
      ]
    ```
  * Please use back slashes in the path string.
  * Please replace the username with your actual user name as well.
* Re-launch Houdini.
* The Hou File Manager GUI can be found when creating a New Pane Tab.
  * ![hou_file_manager_pane_tab](https://github.com/user-attachments/assets/67130c8c-2be0-4c0d-91f1-efdc1c55eea4)

## TODOs
* Logging UI.
