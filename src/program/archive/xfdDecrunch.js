import {xu} from "xu";
import {Program} from "../../Program.js";

export class xfdDecrunch extends Program
{
	website = "http://aminet.net/package/util/pack/xfdmaster";
	flags   = {
		addHeader : "Add an ambk header to the start of the file"
	};

	bin  = "vamos";
	args = async r => [...Program.vamosArgs("xfdDecrunch"), r.inFile(), await r.outFile("outfile")];
	runOptions = {
		timeout : xu.MINUTE,
		
		// Without these, runUtil gets all hung up on the process if there is a password prompt, such as for file: ample/archive/xpk/G-SpellMoon1.0
		stdoutNull    : true,
		stderrNull    : true
	};
	
	post = async r =>
	{
		if(!r.flags.addHeader || !r.f.files.new)
			return;
		
		await r.f.files.new.parallelMap(async file =>
		{
			// Currently not bothering with putting in the bank length, most converters don't seem to care (tried music and picture, both work with 0 for the bank length)
			// Also not bothering putting the proper 'bank number' based on the type of format it is (music/picture/etc)
			// More details: https://www.exotica.org.uk/wiki/AMOS_file_formats
			await Deno.writeFile(file.absolute, Uint8Array.from([0x41, 0x6D, 0x42, 0x6B, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ...(await Deno.readFile(file.absolute))]));
			await file.calcStats();
		});
	};
	renameOut = true;
}
