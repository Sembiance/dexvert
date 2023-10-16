import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class binsciiPrepare extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	unsafe  = true;
	notes   = "Some binscii files have extra whitespace at the beginning of each line, or meta data at the top of the file which causes issues with deark. This program removes that whitespace.";
	exec    = async r =>
	{
		const lines = (await fileUtil.readTextFile(r.inFile({absolute : true})))?.split("\n");
		if(!lines?.length)
			return;

		let seenStart = false;
		lines.filterInPlace(line =>
		{
			if(seenStart)
				return true;

			if(!line.includes("FiLeStArTfIlEsTaRt"))
				return false;
			
			seenStart = true;
			return true;
		});
		
		if(!seenStart)
			return;
		
		const outFilePath = await r.outFile(path.basename(r.inFile()), {absolute : true});
		await fileUtil.writeTextFile(outFilePath, lines.map(line => line.trimStart()).join("\n"));
	};
	renameOut   = false;
	allowDupOut = true;
}
