from platformio.managers.platform import PlatformBase


class H3Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if not variables.get("board"):
            return super(H3Platform, self).configure_default_packages(
                variables, targets)

        build_core = variables.get(
            "board_build.core", self.board_config(variables.get("board")).get(
                "build.core", "arduino"))

        if "arduino" in variables.get(
                "pioframework", []) and build_core != "arduino":

            framework_package = "framework-arduino-avr-%s" % build_core.lower()
            if build_core in ("dtiny", "pro"):
                framework_package = "framework-arduino-avr-digistump"
            elif build_core in ("tiny", "tinymodern"):
                framework_package = "framework-arduino-avr-attiny"

            self.frameworks["arduino"]["package"] = framework_package
            self.packages[framework_package]["optional"] = False
            self.packages["framework-arduino-avr"]["optional"] = True

        upload_protocol = variables.get(
            "upload_protocol",
            self.board_config(variables.get("board")).get(
                "upload.protocol", ""))
        disabled_tool = "tool-micronucleus"
        required_tool = ""

        if upload_protocol == "micronucleus":
            disabled_tool = "tool-avrdude"

        if "fuses" in targets:
            required_tool = "tool-avrdude"

        if required_tool in self.packages:
            self.packages[required_tool]['optional'] = False

        if disabled_tool in self.packages and disabled_tool != required_tool:
            del self.packages[disabled_tool]

        return super(H3Platform, self).configure_default_packages(
            variables, targets)

    def on_run_err(self, line):  # pylint: disable=R0201
        # fix STDERR "flash written" for avrdude
        if "avrdude" in line:
            self.on_run_out(line)
        else:
            PlatformBase.on_run_err(self, line)
