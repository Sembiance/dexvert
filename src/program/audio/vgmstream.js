import {xu} from "xu";
import {Program} from "../../Program.js";
import {C} from "../../C.js";

export class vgmstream extends Program
{
	website = "https://github.com/vgmstream/vgmstream";
	loc     = "local";
	flags   = {
		types : "Specify which format types to treat the input file as. REQUIRED"
	};
	exec = async r =>
	{
		const msg = {inputFilePath : r.inFile({absolute : true}), outputDirPath : r.outDir({absolute : true}), formatid : r.flags.types};
		const result = await xu.fetch(`http://${C.VGMSTREAM_HOST}:${C.VGMSTREAM_PORT}/convert`, {json : msg, asJSON : true});
		if(result?.error)
			r.xlog.error`vgmstream error for types ${r.flags.types}: ${result.error}`;
	};
	chain     = "sox[type:wav]";
	renameOut = {
		alwaysRename : true,
		regex        : /out_(?<num>\d+)\.wav$/,
		renamer      :
		[
			({newName}) => [newName, ".wav"],
			({newName}, {num}) => [newName, "_", num, ".wav"]
		]
	};
}
