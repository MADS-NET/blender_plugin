# blender plugin for MADS

This is a Sink plugin for [MADS](https://github.com/MADS-NET/MADS). 

Sends MADS data to a running Blender instance through the
[NodeOSC](https://github.com/maybites/NodeOSC) add-on. Each incoming JSON frame
is flattened into OSC messages whose addresses are the JSON keypaths:
`{"arm":{"pos":[1,2,3],"open":true}}` becomes `/arm/pos 1 2 3` and
`/arm/open T`. Arrays of scalars become a single multi-argument message, so
they map directly onto vector properties such as `location`.

Look at the documentation for [Blender Python API](https://docs.blender.org/api/current/bpy.types.Object.html#bpy.types.Object) for linking messages field to object properties.

*Required MADS version: 3.0.0.*


## Supported platforms

Currently, the supported platforms are:

* **Linux** 
* **MacOS**
* **Windows**


## Installation

Linux and MacOS:

```bash
cmake -Bbuild -DCMAKE_INSTALL_PREFIX="$(mads -p)"
cmake --build build -j4
sudo cmake --install build
```

Windows:

```powershell
cmake -Bbuild -DCMAKE_INSTALL_PREFIX="$(mads -p)"
cmake --build build --config Release
cmake --install build --config Release
```


## INI settings

The plugin supports the following settings in the INI file:

```ini
[blender]
sub_topic = ["robot"]
host = "127.0.0.1"   # host running Blender with NodeOSC
port = 9001          # NodeOSC input port
use_topic = false    # if true, addresses become /<topic>/<keypath>
```

All settings are optional; if omitted, the default values are used.




## Executable demo

<Explain what happens if the test executable is run>

---

## Blender example: 6-DoF block

Generate an example Blender file with:

```bash
blender --background --factory-startup --python blender/make_scene.py
```

[`blender/block_6dof.blend`](blender/block_6dof.blend) contains a solid block
(`Block`) whose pose is driven by two NodeOSC handlers:

| OSC address | MADS keypath | Blender property | Unit |
|---|---|---|---|
| `/position` | `position: [x, y, z]` | `Block.location` | m |
| `/rotation` | `rotation: [rx, ry, rz]` | `Block.rotation_euler` (XYZ) | rad |

NodeOSC listens on all interfaces, port 9001, and starts automatically when
the file is opened (the NodeOSC add-on, in [`NodeOSC/`](NodeOSC), must be
installed and enabled). Any MADS agent publishing frames like
`{"position": [1, -2, 0.5], "rotation": [0, 0, 1.57]}` moves the block once
this sink, with `use_topic = false`, subscribes to its topic.
