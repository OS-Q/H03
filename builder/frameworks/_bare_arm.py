from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-mthumb",
        "-nostdlib",
        "-fsingle-precision-constant"
    ],

    CXXFLAGS=[
        "-fno-exceptions",
        "-felide-constructors",
        "-fno-rtti",
        "-std=gnu++14"
    ],

    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU"),
        "LAYOUT_US_ENGLISH"
    ],

    RANLIBFLAGS=["-s"],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-Wl,--defsym=__rtc_localtime=$UNIX_TIME",
        "-fsingle-precision-constant"
    ],

    LIBS=["m", "stdc++"]
)

if env.BoardConfig().id_ in ("teensy35", "teensy36"):
    env.Append(
        CCFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LINKFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ]
    )

if "BOARD" in env:
    env.Append(
        CCFLAGS=[
            "-mcpu=%s" % env.BoardConfig().get("build.cpu")
        ],
        LINKFLAGS=[
            "-mcpu=%s" % env.BoardConfig().get("build.cpu")
        ]
    )

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])
