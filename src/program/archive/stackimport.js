import {Program} from "../../Program.js";
import {path} from "std";

export class stackimport extends Program
{
	website       = "https://github.com/uliwitness/stackimport/";
	package       = "dev-util/stackimport";
	bin           = "stackimport";
	args          = r => ["--dumprawblocks", r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	post          = async r =>
	{
		// check to see if we just have a single subdir output, if so, move all files in that one up one dir
		const dirNames = r.f.files.new.map(file => path.dirname(file.rel)).unique();
		if(dirNames.length===1 && dirNames[0].split("/").length===2)
			await r.f.files.new.parallelMap(async file => await file.moveUp(1));
	};
	renameOut = false;
}
