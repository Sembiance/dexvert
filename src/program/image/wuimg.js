import {Program} from "../../Program.js";

export class wuimg extends Program
{
	website   = "https://codeberg.org/kaleido/wuimg";
	package   = "media-gfx/wuimg";
	bin       = "wuconv";
	args      = r => ["-d", r.outDir(), r.inFile()];
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
