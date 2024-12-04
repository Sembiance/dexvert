import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";
import {getWineDriveC} from "../../wineUtil.js";

export class rgssExtractor extends Program
{
	website   = "https://github.com/KatyushaScarlet/RGSS-Extractor";
	loc       = "wine";
	bin       = r => path.join(r.outDir({absolute : true}), "RGSS Extractor.exe");
	args      = r => [r.inFile()];
	exclusive = "rgssExtractor";	// Can't guarantee this is needed, but I've noticed it fail tests sometimes when it's not exclusive
	pre       = async r =>
	{
		// RGGS Extractor will extract all files in the same directory as it's .exe (regardless of cwd), so copy the .exe and it's supporting files to the output directory
		r.binFiles = await fileUtil.tree(path.join(getWineDriveC("win64"), "dexvert", "RGSS-Extractor-v1.0"), {nodir : true, relative : true});
		for(const file of r.binFiles)
			await Deno.copyFile(path.join(getWineDriveC("win64"), "dexvert", "RGSS-Extractor-v1.0", file), path.join(r.outDir({absolute : true}), file));
	};
	postExec = async r =>	// eslint-disable-line sembiance/shorter-arrow-funs
	{
		for(const file of r.binFiles)
			await fileUtil.unlink(path.join(r.outDir({absolute : true}), file));
	};
	wineData = {
		base : "win64",
		arch : "win64"
	};
	renameOut = false;
}
