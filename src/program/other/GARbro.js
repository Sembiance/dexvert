import {xu} from "xu";
import {Program} from "../../Program.js";
import {C} from "../../C.js";

export class GARbro extends Program
{
	website = "https://github.com/shiikwi/GARbro";
	loc     = "local";
	flags   = {
		types : "Specify which format types to treat the input file as. REQUIRED"
	};
	checkForDups = true;
	exec         = async r =>
	{
		const msg = {inputFilePath : r.inFile({absolute : true}), outputDirPath : r.outDir({absolute : true}), formatId : r.flags.types};
		const result = await xu.fetch(`http://${C.GARBRO_HOST}:${C.GARBRO_PORT}/extract`, {json : msg, asJSON : true});
		if(result?.error)
			r.xlog.error`GARbro error for types ${r.flags.codes}: ${result.error}`;
	};
	chain     = r => (r.flags.types.split(",").every(v => v.startsWith("audio:")) ? "sox[type:wav]" : null);
	renameOut = r => !!r.flags.types.split(",").every(v => v.startsWith("audio:") || v.startsWith("image:"));
}
