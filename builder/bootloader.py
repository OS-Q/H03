import sys
from os.path import isfile, join

from SCons.Script import Import, Return

Import("env")

board = env.BoardConfig()
platform = env.PioPlatform()
core = board.get("build.core", "")


def get_suitable_optiboot_binary(framework_dir, board_config):
    mcu = board_config.get("build.mcu", "").lower()
    f_cpu = board_config.get("build.f_cpu", "16000000L").upper()
    uart = board_config.get("hardware.uart", "uart0").upper()
    bootloader_file = "optiboot_flash_%s_%s_%s_%s.hex" % (
        mcu, uart, env.subst("$UPLOAD_SPEED"), f_cpu)
    bootloader_path = join(framework_dir, "bootloaders", "optiboot_flash",
        "bootloaders", "%s" % mcu, "%s" % f_cpu, bootloader_file)

    if isfile(bootloader_path):
        return bootloader_path

    return bootloader_path.replace(".hex", "_BIGBOOT.hex")


common_cmd = [
    "avrdude", "-p", "$BOARD_MCU", "-e", "-C",
    join(platform.get_package_dir("tool-avrdude"), "avrdude.conf"),
    "-c", "$UPLOAD_PROTOCOL", "$UPLOAD_FLAGS"
]

framework_dir = ""
if env.get("PIOFRAMEWORK", []):
    framework_dir = platform.get_package_dir(
        platform.frameworks[env.get("PIOFRAMEWORK")[0]]['package'])

# Common for all bootloaders
lock_bits = board.get("bootloader.lock_bits", "0x0F")
unlock_bits = board.get("bootloader.unlock_bits", "0x3F")
bootloader_path = board.get("bootloader.file", "")

if core in ("MiniCore", "MegaCore", "MightyCore"):
    if not isfile(bootloader_path):
        bootloader_path = get_suitable_optiboot_binary(framework_dir, board)
    fuses_action = env.SConscript("fuses.py", exports="env")
else:
    if not isfile(bootloader_path):
        bootloader_path = join(
            framework_dir, "bootloaders", bootloader_path)

    if not board.get("bootloader", {}):
        sys.stderr.write("Error: missing bootloader configuration!\n")
        env.Exit(1)

    lfuse = board.get("bootloader.lfuse", "")
    hfuse = board.get("bootloader.hfuse", "")
    efuse = board.get("bootloader.efuse", "")

    if not all(f for f in (lfuse, hfuse)):
        sys.stderr.write("Error: Missing bootloader fuses!\n")
        env.Exit(1)

    fuses_cmd = [
        "-Ulock:w:%s:m" % unlock_bits,
        "-Uhfuse:w:%s:m" % hfuse,
        "-Ulfuse:w:%s:m" % lfuse
    ]

    if efuse:
        fuses_cmd.append("-Uefuse:w:%s:m" % efuse)

    fuses_action = env.VerboseAction(
        " ".join(common_cmd + fuses_cmd), "Setting fuses")

if not isfile(bootloader_path):
    sys.stderr.write("Error: Couldn't find bootloader image\n")
    env.Exit(1)

bootloader_flags = [
    '-Uflash:w:"%s":i' % bootloader_path, "-Ulock:w:%s:m" % lock_bits]

bootloader_actions = [
    fuses_action,
    env.VerboseAction(" ".join(common_cmd + bootloader_flags),
                      "Uploading bootloader")
]

Return("bootloader_actions")
