import {Program} from "../../Program.js";
import {DexFile} from "../../DexFile.js";

export class amosTracker2mp3 extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	unsafe  = true;
	exec    = async r =>
	{
		const fileData = await Deno.readFile(r.inFile({absolute : true}));

		// Format: https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format
		if(fileData.length<22 || fileData.getString(0, 4)!=="AmBk" || fileData.getString(12, 8)!=="Tracker ")
			return;
		
		const outFilePath = await r.outFile(`${fileData.getString(20, 20).replaceAll("\0", "")}.mod`, {absolute : true});

		// https://www.exotica.org.uk/wiki/Protracker
		// It's important that we add the .mod extension so programs like awaveStudio can convert it properly
		await Deno.writeFile(outFilePath, fileData.slice(20));

		// Now that we have an intermediate mod file, get our meta info from that
		const musicInfoR = await Program.runProgram("musicInfo", await DexFile.create({root : r.f.root, absolute : outFilePath}), {xlog : r.xlog, autoUnlink : true});
		Object.assign(r.meta, musicInfoR.meta);
	};
	renameOut = false;
	chain     = "dexvert";
}
