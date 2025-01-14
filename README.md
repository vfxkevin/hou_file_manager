# Houdini File Path Manager
A GUI tool and central place for managing all Houdini file paths (textures, images, caches, geometries) of node parameters.
![hou_file_manager_gui_01](https://github.com/user-attachments/assets/72080231-e58c-43fc-b32f-6c56a8f03f2f)


## Tutorials
* Youtube: https://youtu.be/LoOPm2v3AoQ
  * NOTE: Installation can be automated now! The Youtube video is only showing the manual method. So for the recommended installation method, please refer to the steps in this document below.


## Functionalities:
* Refresh button for refreshing the Node View when Houdini scene is changed.
  * Node View selection will be cleared once Refresh button is clicked.
  * Parameter View will be cleared as well.
* Search in a path for nodes with file parmaters (image or geometry).
  * Use the scene browser button to choose a node. Then the search will be conducted recursively under the node.
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
        * `* ^*shader*` for any names without `shader` in it.
  * Node Type: Houdini single name patterns.
  * Parameter Name: Houdini multi name patterns, like *, ^ and combinations.
    * Refer to above Node Name multi name patterns.
  * Parameter File Type: `Image` or `Geometry`.
* Node View
  * It only shows the nodes based on the search results.
  * The nodes with file parametes that match the filters will be highlighted in red color.
  * Users can select nodes in the Node View, and so their parameters that match the filters will be shown in the Parameter View.
    * (NOTE: This won't affect Houdini current node selection in Network View, unless double click on a node in Node View.)
    * Left Mouse Button (LMB) click to select single node.
    * LMB click and drag to select multiple nodes.
    * Ctrl + LMB to toggle selection of individual node.
    * Shift + LMB click on the start and end node to select a range of nodes.
  * Double-clicking on a node will set current selected node to it in the Network Editor.
    * (Note: it will affect Houdini current node selection in the Network View.)
* Parameter View
  * The file parmaeters will be shown in the Parameter View for the selected nodes in the Node View.
    * Not the actual selected nodes in Network Editor.
  * Each file parameter item in the Parameter View has:
    * A `File Choose` button to choose a file for it (the dialog has image preview on), and
    * A `Preview` button to preview the image in MPlay minimal mode.
  * The Raw Value of the file parameter in the Parameter View can be edited in place by double-clicking on it.
* Tools UI
  * Files in the Parameter View can be batch processed, and the Raw Value file paths of the parmaeters will be updated to the new paths. Currently supported actions are:
    * `Copy` : To copy the files specified in the parameters to a destination directory, and then update the parameter file paths to the new paths. But if the files specified in the parameters don't exist or the copying action failed, nothing will be copied and parameters won't be updated either.
    * `Move` : To move the files specified in the parameters to a destination directory, and then update the parameter file paths to the new paths. But if the files specified in the parameters don't exist or the moving action failed, nothing will be moved and parameters won't be updated either.
    * `Repath` : To change the directory paths of the files specified in the parameters to a new desination directory. It just simply changes the file path values of the parameters, and won't check if the file paths are really pointing to real files or not.
  * `<UDIM>` sequence file paths are supported.
  * Time dependent sequence paths with `$F` or `${F}` are supported. The `$F` or `${F}` can have zero paddings, such as `$F4`, `$F6`, `${F4}` etc.


## Installation
1. Go to [Releases](https://github.com/vfxkevin/hou_file_manager/releases) and download the **source code zip file** from the latest release.
   * For example, release `v0.1.x` is downloaded.
2. Two methods to install the package:
   * **Method A (RECOMMENDED)** - Automated installation using Package Archive
     * In Houdini, launch Package Browser
       ![launch_package_browser](https://github.com/user-attachments/assets/8c1b9d61-441b-464e-8198-2356fbefb2db)
     * In File menu, run Install Package Archive
       ![package_browser_install_archive](https://github.com/user-attachments/assets/87b9abf6-8535-4956-935d-db23772a491c)
     * Select the zip file in the previous step, and install to a sub-folder inside Houdini Packages folder.
       ![install_package_archive](https://github.com/user-attachments/assets/a35f4b93-9720-4d9e-9e96-2867643d1da3)
     * Ensure the package is installed and loaded
       ![package_loaded](https://github.com/user-attachments/assets/83e0e8a1-002a-4d5f-974b-cb9488e7ac6b)
   * **Method B** - Manual installtion (if customised installation needed, otherwise skip to step 3)
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
3. Must re-start Houdini to load the tools.


## Launch Hou File Manager Tool
There are 3 methods to launch the GUI:
* Load the `File Manager` shelf and use the first `File Manager` button to launch it.
  * ![file_manager_shelf](https://github.com/user-attachments/assets/3d872471-af7b-479d-8a10-9386d30c448f)
* Add a `New Pane Tab` of `Hou File Manager` to the main desktop.
  * ![hou_file_manager_pane_tab](https://github.com/user-attachments/assets/67130c8c-2be0-4c0d-91f1-efdc1c55eea4)
* In Network Editor, press hotkey `m` to load out quick radial menu, and choose `File Manager`.
  * ![network_editor_radial_menu](https://github.com/user-attachments/assets/9c3f813d-1e7f-4c24-a063-31749b3733d0)

## Other Tools
* Other useful tools on the shelf/raidial menu:
  * Out Null
    * Create `Null` nodes (named OUT) and connect them to the outputs of the corresponding selected nodes.
  * Obj Merge
    * Create `Object Merge` nodes, put them on the side of the corresponding selected nodes, and set the `Object` parameter paths to the corresponding selected nodes.
  * Merge
    * Create a `Merge` node and connect all the selected nodes to the input of the Merge node.
  * Switch
    * Create a `Switch` node and connect all the selected nodes to the input of the Switch node.
  * Geometry
    * Create a `Geometry` node. But it will only work at `/obj` level.
  * File Cache
    * Create `File Cache` nodes and connect them to the outputs of the corresponding selected nodes.
  * Transform
    * Create `Transnform` nodes and connect them to the outputs of the correspoding selected nodes. 

## TODOs
* Logging UI.
* Preview geometry file(s).
