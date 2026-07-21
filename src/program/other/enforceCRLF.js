import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class enforceCRLF extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	unsafe  = true;
	loc     = "local";
	exec    = async r =>
	{
		if(r.f.input.size>xu.MB*25)
			return;

		const fileData = await Deno.readFile(r.inFile({absolute : true}));
		if(fileData.indexOfX([0x0D, 0x0A])!==-1)
			return;

		const outDirPath = r.outDir({absolute : true});
		const outFilePath = await fileUtil.genTempPath(outDirPath, path.basename(r.inFile({absolute : true})));

		const newBytes = [];
		let lastByte = null;
		for(const byte of fileData)
		{
			if(byte===0x0A && lastByte!==0x0D)
				newBytes.push(0x0D);	// lone LF -> CRLF
			if(lastByte===0x0D && byte!==0x0A)
				newBytes.push(0x0A);	// lone CR -> CRLF
			newBytes.push(byte);
			lastByte = byte;
		}
		if(lastByte===0x0D)
			newBytes.push(0x0A);	// lone CR at EOF -> CRLF

		await Deno.writeFile(outFilePath, new Uint8Array(newBytes));
	};
	renameIn  = false;	// RunState.originalInput would be lost and dexvert should be able to handle any incoming filename
	renameOut = false;
}
