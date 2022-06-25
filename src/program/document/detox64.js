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
		
		// a 1 line BASIC program is not only un-interesting, but is also usually a false conversion
		if(lines.length===1)
			return false;

		if(lines.some(line => !line.startsWith("0") && line.trim().length>0 && !(/^\d+\s[^\n]+$/).test(line.trim())))
			return false;
		
		// verify that all our lines are numbers and are in ascending order
		const lineNumbers = lines.map(line => line.trim().split(" ")).filter(parts => parts.length===2).map(parts => parts[0]);
		let prevLineNumber = -1;
		for(const lineNumber of lineNumbers)
		{
			if(!lineNumber.isNumber() || +lineNumber<=prevLineNumber)
				return false;

			prevLineNumber = +lineNumber;
		}

		return true;
	};

	renameOut  = true;
}
