import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

const progBasePath = Program.binPath("amiga-bitmap-font-tools");

export class amigaBitmapFontContentToOTF extends Program
{
	website    = "https://github.com/smugpie/amiga-bitmap-font-tools";
	bin        = path.join(progBasePath, "env/bin/python3");
	args       = async r =>
	{
		r.ufoTmpPath = await fileUtil.genTempPath(undefined, ".ufo");
		return [path.join(progBasePath, "openAmigaFont.py"), "-i", r.inFile(), "-o", await r.outFile("out.otf"), "-f", "otf", "-t", r.ufoTmpPath];
	};
	runOptions = {env : {VIRTUAL_ENV : path.join(progBasePath, "env")}};
	renameOut  = {
		alwaysRename : true,
		renamer      : [({newName, originalInput}) => (originalInput ? [path.basename(originalInput.dir), "-", originalInput.name, ".otf"] : [newName, ".otf"])]
	};
	postExec = async r => await fileUtil.unlink(r.ufoTmpPath, {recursive : true});
	notes = "I modified openAmigaFont.py to support specifying a tmp file path, so I can run multiple copies of this program at the same time without collisions";
}
