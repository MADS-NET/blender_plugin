# blender — working notes for AI coding agents

This is a **MADS sink plugin** written in C++17.

Framework context — the plugin lifecycle, the order in which the host agent
calls each method, what every return value does, how settings reach the plugin,
topics, blobs, testing, deployment and protocol migration — is in the
`mads-plugin` skill under [`.claude/skills/mads-plugin/`](.claude/skills/mads-plugin/SKILL.md).
**Read `SKILL.md` before changing plugin code**, and follow its `reference/`
files rather than inferring host behaviour from the template comments.

Regenerate that skill for a newer MADS with `mads plugin --update`.

## This plugin

Bridges MADS data into a running Blender instance through the
[NodeOSC](https://github.com/maybites/NodeOSC) add-on. Every incoming frame is
flattened into OSC messages sent over UDP: the OSC address is the JSON keypath,
so in NodeOSC a handler on `/pos` or `/arm/joint/0` drives a Blender property.

- Behavior: **sink** — host agent `mads sink`
- Class: `BlenderPlugin` in [`src/blender.cpp`](src/blender.cpp)
- Driver name: `blender` — must stay equal to the CMake target name, so that `kind()` and the file stem agree
- INI section: `[blender]` (or whatever `-n` selects at run time)

## Parameters

Keep this table and the README in sync — it is the plugin's public interface.
Do not name a parameter `prefix`: the host injects that key.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `host` | string | `"127.0.0.1"` | Host running Blender/NodeOSC (name or IP) |
| `port` | int | `9001` | NodeOSC input port |
| `use_topic` | bool | `false` | Prepend the MADS topic to every address (`/<topic>/<keypath>`) |

## Output frames

Consumes any JSON frame; publishes nothing on MADS. Mapping to OSC:

- scalar leaf → one message, address = keypath: `{"a":{"b":1.5}}` → `/a/b 1.5`
- array of scalars → one message with one arg per element (fits Blender vector
  properties): `{"pos":[1,2,3]}` → `/pos 1 2 3`
- other arrays → recurse with the index as path element: `/list/0/x`
- types: float → `f`, int → `i` (`h` beyond int32), bool → `T`/`F`, string → `s`;
  `null` is skipped
- one UDP datagram per message; MADS metadata (`timestamp`, `hostname`, ...) is
  sent too, ignore it in NodeOSC if not needed

## Conventions for this project

- C++17, built with CMake; LLVM formatting, two-space indent.
- `CamelCase` for classes and namespaces, `snake_case` for methods and
  variables, `_leading_underscore` for private members, declared last.
- Do not add third-party dependencies without asking. `nlohmann/json` is
  already available, and the plugin base classes also provide a `SerialPort`
  helper in `serialport.hpp`.
- All plugin logic must be reachable from the test `main()` at the bottom of
  the source file, and that test must be deterministic and self-checking:
  assert on both the returned status and the payload, and exit non-zero on
  failure.
- An exception must never escape a plugin method: catch it, set `_error` and
  return `return_type::error`.
- Never block, sleep or busy-wait inside a plugin method.

## Build and test

```sh
cmake -Bbuild -DCMAKE_INSTALL_PREFIX="$(mads -p)"
cmake --build build -j4
./build/blender                       # the standalone test driver
mads inspect_plugin build/blender.plugin
mads sink build/blender.plugin
```
