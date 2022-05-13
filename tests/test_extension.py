import re
import unittest
import markdown
from biovis_media_extension.extension import BioVisPluginExtension

class TestUtils(unittest.TestCase):
    plugin = BioVisPluginExtension(configs={})

    def test_invalid_plugin(self):
        text = """
        @invalid-plugin()
        """
        output = markdown.markdown(text, extensions=[self.plugin])
        matched = re.match("<div class='alert alert-danger' role='alert'>", output) != None
        self.assertEqual(matched, True)

if __name__ == '__main__':
    unittest.main()
