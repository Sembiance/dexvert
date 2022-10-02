import {Program} from "../../Program.js";

export class unApple2Icons extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("unApple2Icons.js"), "--", r.inFile(), r.outDir());
	runOptions = ({env : Program.denoEnv()});
	renameOut  = {
		alwaysRename : true,
		regex        : /out_(?<num>\d+)\.ppm$/,
		renamer      : [({newName}, {num}) => [newName, "_", num, ".ppm"]]
	};
	chain = "convert";
}
