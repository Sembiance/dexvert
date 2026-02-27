import {xu} from "xu";
import {Program} from "../../Program.js";
import {C} from "../../C.js";

export class gameextractor extends Program
{
	website = "https://sourceforge.net/projects/gameextractor/files/";
	loc     = "local";
	flags   = {
		codes : "Specify which format code to treat the input file as, default: Let gameextractor decide"
	};
	checkForDups = true;
	exec         = async r =>
	{
		const msg = {inputFilePath : r.inFile({absolute : true}), outputDirPath : r.outDir({absolute : true})};
		if(r.flags.codes?.length)
			msg.codes = r.flags.codes.toString().split(",");

		const result = await xu.fetch(`http://${C.GAMEEXTRACTOR_HOST}:${C.GAMEEXTRACTOR_PORT}/extract`, {json : msg, asJSON : true});
		if(result?.error)
			r.xlog.error`GameExtractor error for codes ${r.flags.codes}: ${result.error}`;
	};
	renameOut = false;
}
