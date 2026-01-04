import {xu} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";

export class gimp extends Program
{
	website = "https://gimp.org";
	package = "media-gfx/gimp";
	bin     = "gimp";
	flags   = {
		layers   : "Output all the layers, rather than just 1 single flattened image"
	};
	pre = async r =>
	{
		// DOCUMENTATION: Open gimp and go to Help->Procedure Browser
		// In there you can look at the various procedures that GIMP has available along with which named arguments to pass and their types
		// An up to date example of the latest python code is: file:///usr/lib64/gimp/2.99/plug-ins/file-openraster/file-openraster.py
		await fileUtil.writeTextFile(path.join(r.f.root, "dexvert.py"), `import gi
import os
from gi.repository import GObject, Gimp, Gio

def loadAndSave(inPath, outPath):
	pdb = Gimp.get_pdb()

	loadProc = pdb.lookup_procedure("gimp-file-load")
	loadConfig = loadProc.create_config()
	loadConfig.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
	loadConfig.set_property("file", Gio.File.new_for_path(inPath))
	image = loadProc.run(loadConfig).index(1)

	if type(image) is Gimp.Image:
		saveProc = pdb.lookup_procedure("file-png-export")
		saveConfig = saveProc.create_config()
		saveConfig.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
		saveConfig.set_property("image", image)
		saveConfig.set_property("file", Gio.File.new_for_path(outPath))
		saveConfig.set_property("interlaced", False)
		saveConfig.set_property("compression", 9)
		saveConfig.set_property("bkgd", False)
		saveConfig.set_property("offs", False)
		saveConfig.set_property("phys", False)
		saveConfig.set_property("time", False)
		saveConfig.set_property("save-transparent", False)
		saveConfig.set_property("optimize-palette", False)
		saveProc.run(saveConfig)

	quitProc = pdb.lookup_procedure("gimp-quit")
	quitConfig = quitProc.create_config()
	quitConfig.set_property("force", True)
	quitProc.run(quitConfig)

def loadAndSaveLayers(inPath, outDir):
    # Ensure the output directory exists
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    pdb = Gimp.get_pdb()

    # Load the source image (e.g., .gih, .psd, .xcf)
    loadProc = pdb.lookup_procedure("gimp-file-load")
    loadConfig = loadProc.create_config()
    loadConfig.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    loadConfig.set_property("file", Gio.File.new_for_path(inPath))
    
    result = loadProc.run(loadConfig)
    image = result.index(1)

    if isinstance(image, Gimp.Image):
        # image.get_layers() returns the list of layers
        layers = image.get_layers()
        
        for i, layer in enumerate(layers):
            # Format filename: 01.png, 02.png...
            filename = "{:02d}.png".format(i + 1)
            outPath = os.path.join(outDir, filename)
            
            # 1. Create a temporary image the size of this specific layer
            temp_image = Gimp.Image.new(
                layer.get_width(), 
                layer.get_height(), 
                image.get_base_type()
            )
            
            # 2. Copy the layer content to the new image
            new_layer = Gimp.Layer.new_from_drawable(layer, temp_image)
            temp_image.insert_layer(new_layer, None, 0)

            # 3. Setup PNG Export using the same properties that worked for you
            saveProc = pdb.lookup_procedure("file-png-export")
            saveConfig = saveProc.create_config()
            saveConfig.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
            saveConfig.set_property("image", temp_image)
            saveConfig.set_property("file", Gio.File.new_for_path(outPath))
            
            # Your preferred PNG settings
            saveConfig.set_property("interlaced", False)
            saveConfig.set_property("compression", 9)
            saveConfig.set_property("bkgd", False)
            saveConfig.set_property("offs", False)
            saveConfig.set_property("phys", False)
            saveConfig.set_property("time", False)
            saveConfig.set_property("save-transparent", True)
            saveConfig.set_property("optimize-palette", False)
            
            # Execute export
            saveProc.run(saveConfig)
            
            # 4. Cleanup temporary image from memory
            temp_image.delete()

    # Quit GIMP
    quitProc = pdb.lookup_procedure("gimp-quit")
    quitConfig = quitProc.create_config()
    quitConfig.set_property("force", True)
    quitProc.run(quitConfig)`);
	};

	args       = async r => ["-ni", "--batch-interpreter", "python-fu-eval", "-b", `import sys;sys.path=['.']+sys.path;import dexvert;dexvert.loadAndSave${r.flags.layers ? "Layers" : ""}('${r.inFile()}', '${r.flags.layers ? r.outDir() : await r.outFile("out.png")}')`];
	runOptions = ({timeout : xu.MINUTE*2, virtualX : true});
	renameOut  = true;
}
