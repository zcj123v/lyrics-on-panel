import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
KCONFIG_PATH = REPO_ROOT / "kde/v2/contents/config/main.xml"
MAIN_QML_PATH = REPO_ROOT / "kde/v2/contents/ui/main.qml"
CONFIG_QML_PATH = REPO_ROOT / "kde/v2/contents/ui/configGeneral.qml"
KCFG_NAMESPACE = {"kcfg": "http://www.kde.org/standards/kcfg/1.0"}


class PlasmaThemeConfigurationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kconfig = ET.parse(KCONFIG_PATH).getroot()
        cls.main_qml = MAIN_QML_PATH.read_text(encoding="utf-8")
        cls.config_qml = CONFIG_QML_PATH.read_text(encoding="utf-8")

    def kconfig_entry(self, name):
        entry = self.kconfig.find(
            f".//kcfg:entry[@name='{name}']",
            KCFG_NAMESPACE,
        )
        self.assertIsNotNone(entry, f"缺少 KConfig 项：{name}")
        return entry

    def test_color_default_is_a_literal_kconfig_color(self):
        default = self.kconfig_entry("lyricTextColor").find(
            "kcfg:default",
            KCFG_NAMESPACE,
        )
        self.assertIsNotNone(default)
        self.assertRegex(default.text or "", r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")

    def test_theme_colors_are_enabled_by_default(self):
        default = self.kconfig_entry("useCustomColorsChecked").find(
            "kcfg:default",
            KCFG_NAMESPACE,
        )
        self.assertIsNotNone(default)
        self.assertEqual((default.text or "").strip(), "false")

    def test_lyrics_and_controls_use_runtime_theme_color(self):
        self.assertRegex(
            self.main_qml,
            re.compile(
                r"property color effectiveLyricTextColor:.*?"
                r"Kirigami\.Theme\.textColor",
                re.DOTALL,
            ),
        )
        self.assertNotIn("PlasmaCore.Theme.textColor", self.main_qml)
        self.assertIn("color: effectiveLyricTextColor", self.main_qml)
        self.assertIn("property color effectiveMediaControlIconColor:", self.main_qml)
        self.assertGreaterEqual(self.main_qml.count("Kirigami.Icon {"), 5)
        self.assertGreaterEqual(
            self.main_qml.count("color: effectiveMediaControlIconColor"),
            4,
        )

    def test_configuration_keeps_an_explicit_custom_color_override(self):
        self.assertIn("cfg_useCustomColorsChecked", self.config_qml)
        self.assertIn("id: useCustomColorsChecked", self.config_qml)
        self.assertIn("enabled: useCustomColorsChecked.checked", self.config_qml)


if __name__ == "__main__":
    unittest.main()
