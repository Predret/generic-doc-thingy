const treejson = await fetch("/generated/tree.json");
const treedata = await treejson.json();

console.log(treedata)
console.log(window.location.pathname)

const current_path = window.location.pathname

const FileInstance = {
  Data: class {
    constructor(data) {
      this.type = data.type;
      this.path = data.path;
      this.mod_time = data.mod_time;
    }
  },
  DocFile: class extends FileInstance.Data {
    constructor(data) {
      super(data);
      this.headers = data.headers ?? [];
    }
  },
  Folder: class extends FileInstance.Data {
    constructor(data) {
      super(data);
      this.contents = (data.contents ?? []).map(child => FileInstance.deserialize(child))
    }
  },
  Project: class extends FileInstance.Folder {
    constructor(data) {
      super(data);
      this.icon = data.icon;
    }
  },
  deserialize: function(data) {
    switch (data.type) {
      case "docfile": return new FileInstance.DocFile(data);
      case "folder": return new FileInstance.DocFile(data);
      case "project": return new FileInstance.Project(data);
      default: throw new Error("Invalid type: " + data.type)
    }
  }
}


function get_name(path)
{
  return path.slice(path.lastIndexOf("/") + 1)
}
function get_parent(path)
{
  const cleanPath = path.replace(/\/+$/, "");
  const slash = cleanPath.lastIndexOf("/");
  return slash === -1 ? "" : cleanPath.slice(0, slash);
}

function get_project(path)
{
  if (!path.lastIndexOf("/"))
  {
    get_project(get_parent(path));
  }

}


if (!current_path.startsWith("/html/docs/"))
{
  console.log("outside");
}


// class FileTree extends HTMLElement {
//   connectedCallBack() {
//     this.innerHTML = `

//       `
//   }
// }

// customElements.define(name, constructor)
