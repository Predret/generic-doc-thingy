# Plan for documentationtemplate:


## Generated folder
+ Generated folder contains the entire tree and search-related objects.
+ project folder and search folder are generated

  ### project folder:
  + Contains `name.data.json`.
    *Where name is the ID.*
  + Each .json will contain a project, it's path, every folder inside it, every docfile inside it, and every header's name in every docfile. (not including other project folders)
  + it's .json will also contain the place the project was registered (the directory above the directory containing `_proj.json`) (In case the user got to someplace without any information on how they got there)

  ### search folder:
  + Contains `name.searchNNNN.json`.
    *Where name is the project ID and NNNN is a number.*
  + Each .json will contain a search chunk for a project with every folder inside it, excluding other project folders, essentially just considering them as a hyperlink, or tag, to a different place. 
  + The json will also contain a "next" variable, pointing to the next search path if there is one.
  + If there is no next search path, it is simply null
  + The N stands for the current search. 4 Ns to make it clear that it's a number.
  + A specific variable will determine the max size of a json. This is to make memory not spike, and to keep max file sizes into account.

## Project linking
+ `_proj.json` files belong directly inside the folder the project is supposed to be in.
+ A project's name inherits from the folder above the `_proj.json`.
+ A `_proj.json` file creates a project in the project folder. (and the search folder)
+ Going to a project through a `_proj.json` works by simply entering the `_proj.json`'s directory.
+ A `_proj.json` can contain an icon, but it is optional.
+ Projects function differently from normal folders inside a project. Unlike a folder, a project doesn't belong to another project. (It somewhat does, but I will explain more on this)
+ Another way of entering a project is through a `_linkproj.json`.
+ `_linkproj.json` does not define it's own project. It simply links to an existing project. Every project has a globally unique ID.
+ `_linkproj.json`s should **not** be put in their own directory, as they aren't defining a project.
+ A `_linkproj.json` simply states, that there is a project by some id (stated inside it) and it can be looked up through the project folder. (requires a proj.json)
+ `_linkproj.json`s open by checking if each ID exists in the project folder, and reading where it is.
+ `_linkproj.json` has it's ids in an array. Not as a singular id.
+ If a `_linkproj.json` exists with no linked project, an error will occur in the build. Please check the build logs.
+ **PROJECT IDs MUST BE GLOBALLY UNIQUE**
+ **`_linkproj`'S IDs MUST MATCH WITH EXISTING PROJECT'S IDs**
+ **`_linkproj`'S ID(s) MUST BE IN AN ARRAY. WITH EACH ITEM BEING AN ID**
  ### _proj.json example: 

    myprojectfolder:
      _proj.json

  (inside)

    {
      "id": "hjanzx2131asd",
      "icon": "iconpath"
    }

  ### _linkproj.json example

  (inside)

    {
      "ids":\["hjanzx2131asd", "adkladns1lka"]
    }
