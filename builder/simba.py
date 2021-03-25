from os.path import join, sep

from SCons.Script import DefaultEnvironment, SConscript

from platformio.builder.tools import platformio as platformio_tool

#
# Backward compatibility with PlatformIO 2.0
#
platformio_tool.SRC_DEFAULT_FILTER = " ".join([
    "+<*>", "-<.git%s>" % sep, "-<svn%s>" % sep,
    "-<example%s>" % sep, "-<examples%s>" % sep,
    "-<test%s>" % sep, "-<tests%s>" % sep
])


def LookupSources(env, variant_dir, src_dir, duplicate=True, src_filter=None):
    return env.CollectBuildFiles(variant_dir, src_dir, src_filter, duplicate)


def VariantDirWrap(env, variant_dir, src_dir, duplicate=False):
    env.VariantDir(variant_dir, src_dir, duplicate)


env = DefaultEnvironment()

env.AddMethod(LookupSources)
env.AddMethod(VariantDirWrap)

env.Append(CPPDEFINES=[("F_CPU", "$BOARD_F_CPU")])

env.Replace(
    PLATFORMFW_DIR=env.PioPlatform().get_package_dir("simba")
)

SConscript(
    [env.subst(join("$PLATFORMFW_DIR", "make", "platformio.sconscript"))])
