import {xu} from "xu";
import {Program} from "../../Program.js";
import {C} from "../../C.js";

export class gameextractor extends Program
{
	website = "https://sourceforge.net/projects/gameextractor/files/";
	loc     = "local";
	flags   = {
		codes : "Specify which format code to treat the input file as. REQUIRED"
	};
	checkForDups = true;
	exec         = async r =>
	{
		const result = await xu.fetch(`http://${C.GAMEEXTRACTOR_HOST}:${C.GAMEEXTRACTOR_PORT}/extract`, {json : {inputFilePath : r.inFile({absolute : true}), outputDirPath : r.outDir({absolute : true}), codes : r.flags.codes.toString().split(",")}, asJSON : true});
		if(result?.error)
			r.xlog.error`GameExtractor error for codes ${r.flags.codes}: ${result.error}`;
	};
	verify    = (r, dexFile) => dexFile.size<Math.max(r.f.input.size*3, xu.MB*5);		// some files are mistakenly identified as zlib and HUGE files are created
	renameOut = false;
}
