import {xu} from "xu";
import {Program} from "../../Program.js";

const _BIN_FILES = [
	"RGSS Extractor.exe",
	"RGSS Extractor.exe.config",
	"RGSS Extractor.pdb"
];

export class rgssExtractor extends Program
{
	website   = "https://github.com/KatyushaScarlet/RGSS-Extractor";
	loc       = "win7";
	bin       = `c:\\out\\${_BIN_FILES[0]}`;
	args      = r => [r.inFile()];
	osData    = {
		// RGGS Extractor will extract all files in the same directory as it's .exe (regardless of cwd), so copy the .exe and it's supporting files to the output directory
		scriptPre : _BIN_FILES.map(v => `FileCopy("c:\\dexvert\\RGSS-Extractor-v1.0\\${v}", "c:\\out\\${v}");`).join("\n"),
		script : `
				WaitForStableDirCount("c:\\out", ${xu.SECOND*10}, ${xu.MINUTE*5})
				${_BIN_FILES.map(v => `FileDelete("c:\\out\\${v}");`).join("\n")}`
	};
	renameOut = false;
}
