import {Program} from "../../Program.js";

export class wuimg extends Program
{
	website = "https://codeberg.org/kaleido/wuimg";
	package = "media-gfx/wuimg";
	flags   = {
		format : "Specify which format to treat the input file as. Run `wuconv --fmts` for a list. Default: Let wuconv decide"
	};
	bin       = "wuconv";
	args      = r => [...(r.flags.format ? ["-t", r.flags.format] : []), "-d", r.outDir(), r.inFile()];
	renameOut = {
		alwaysRename : true,
		regex        : /_(?<num>\d{5})(?<ext>\.pam)$/,
		renamer      :
		[
			({newName}) => [newName, ".pam"],
			({newName}, {num, ext}) => [newName, " ", num, ext]
		]
	};
	chain = "convert[skipVerify][bulkCopyOut]";
}
