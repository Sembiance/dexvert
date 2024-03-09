import unittest
from xfile_parser import XFileParser


class TestStringMethods(unittest.TestCase):

    def load(self, filename):
        with open(filename, 'br') as f:
            buffer = f.read()
        parser = XFileParser(buffer)
        scene = parser.getImportedData()
        return scene

    def test_anim_test(self):
        scene = self.load('models/anim_test.x')
        mesh = scene.rootNode.children[0].children[0].meshes[0]
        self.assertEqual(scene.anims[0].name, "cylinder_test")
        self.assertEqual(len(mesh.positions), 1720)

    def test_BCN_Epileptic(self):
        scene = self.load('models/BCN_Epileptic.X')
        mesh = scene.rootNode.children[1].meshes[0]
        self.assertEqual(len(mesh.positions), 648)

    def test_fromtruespace_bin32(self):
        scene = self.load('models/fromtruespace_bin32.x')
        mesh = scene.rootNode.meshes[0]
        self.assertEqual(len(mesh.positions), 4132)

    def test_kwxport_test_cubewithvcolors(self):
        scene = self.load('models/kwxport_test_cubewithvcolors.x')
        mesh = scene.rootNode.meshes[0]
        self.assertEqual(len(mesh.positions), 24)
        self.assertEqual(len(mesh.colors[0]), 24)

    # def test_OV_GetNextToken(self):
        #mesh = self.load('models/OV_GetNextToken')
        # pass

    def test_test(self):
        scene = self.load('models/test.x')
        mesh = scene.rootNode.meshes[0]
        self.assertEqual(len(mesh.positions), 24)

    def test_test_cube_compressed(self):
        scene = self.load('models/test_cube_compressed.x')
        mesh = scene.rootNode.children[0].meshes[0]
        self.assertEqual(len(mesh.positions), 24)

    def test_test_cube_text(self):
        scene = self.load('models/test_cube_text.x')
        mesh = scene.rootNode.children[0].meshes[0]
        self.assertEqual(len(mesh.positions), 24)

    def test_test_format_detection(self):
        scene = self.load('models/TestFormatDetection')
        mesh = scene.rootNode.meshes[0]
        self.assertEqual(len(mesh.positions), 24)

    def test_Testwuson(self):
        scene = self.load('models/Testwuson.X')
        mesh = scene.rootNode.children[0].meshes[0]
        self.assertEqual(len(mesh.positions), 3205)

    def test_dwarf(self):
        scene = self.load('models-nonbsd/dwarf.X')
        mesh = scene.rootNode.children[1].meshes[0]
        self.assertEqual(scene.anims[0].name, "AnimationSet0")
        self.assertEqual(len(mesh.positions), 1479)


if __name__ == '__main__':
    unittest.main()
