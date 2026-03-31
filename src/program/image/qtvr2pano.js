import {Program} from "../../Program.js";
import {path} from "std";

export class qtvr2pano extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	bin       = "python3";
	args      = r => [path.join(Program.binPath("qtvr2pano"), "qtvr2pano.py"), r.inFile({absolute : true}), r.outDir({absolute : true})];
	verify    = (r, dexFile) => !!dexFile.base.endsWith(".jpg");
	renameOut = {
		alwaysRename : true,
		regex        : /(?<num>\d+)\.jpg$/,
		renamer      :
		[
			({newName}) => [newName, ".jpg"],
			({newName}, {num}) => [newName, "_", num, ".jpg"]
		]
	};
}
