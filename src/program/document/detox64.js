import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class detox64 extends Program
{
	website    = "https://github.com/vroby65/detox64";
	package    = "dev-util/detox64";
	bin        = "detox64";
	unsafe     = true;
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});

	// ensure the lines match the expected output
	verify = async (r, dexFile) =>
	{
		const lines = (new TextDecoder("utf-8").decode(await fileUtil.readFileBytes(dexFile.absolute, Math.min(dexFile.size, xu.KB*100)))).trim().split("\n").filter(v => !!v);
		if(lines.some(line => !line.startsWith("0") && line.trim().length>0 && !(/^\d+\s[^\n]+$/).test(line.trim())))
			return false;

		return true;
	};

	renameOut  = true;
}
