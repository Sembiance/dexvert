import {xu} from "xu";
import {Program} from "../../Program.js";
import {C} from "../../C.js";

export class dragonUnpacker extends Program
{
	website = "https://github.com/elbereth/DragonUnPACKer";
	loc     = "local";
	flags   = {
		types : "Specify which format types to treat the input file as. REQUIRED"
	};
	checkForDups = true;
	exec         = async r =>
	{
		const msg = {inputFilePath : r.inFile({absolute : true}), outputDirPath : r.outDir({absolute : true}), formatid : r.flags.types};
		const result = await xu.fetch(`http://${C.DRAGON_UNPACKER_HOST}:${C.DRAGON_UNPACKER_PORT}/extract`, {json : msg, asJSON : true});
		if(result?.error)
			r.xlog.error`dragonUnpacker error for types ${r.flags.codes}: ${result.error}`;
	};
	renameOut = false;
}
