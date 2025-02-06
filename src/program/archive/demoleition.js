import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class demoleition extends Program
{
	website  = "https://lifeinhex.com/updated-molebox-unpacker/";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\dexvert\\demoleition.exe";
	args     = r => [`c:\\out\\${path.basename(r.inFile())}`];
	osData   = r => ({
		scriptPre : `
			FileCopy("c:\\in\\${path.basename(r.inFile())}", "c:\\out\\${path.basename(r.inFile())}");`,
		script : `
			WindowRequire("de-mole-ition v0.65", "", 10)
			WaitForStableFileSize("c:\\out\\${path.basename(r.inFile(), path.extname(r.inFile()))}_unpacked${path.extname(r.inFile())}", ${xu.SECOND*5}, ${xu.SECOND*30})
			FileDelete("c:\\out\\${path.basename(r.inFile())}")`
	});
	renameOut = false;
}
