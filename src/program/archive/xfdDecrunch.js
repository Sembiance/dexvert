import {Program} from "../../Program.js";

export class xfdDecrunch extends Program
{
	website = "http://aminet.net/package/util/pack/xfdmaster";
	loc     = "amiga";
	flags   = {
		addHeader : "Add an ambk header to the start of the file"
	};

	bin  = "xfdDecrunch";
	args = r => [r.inFile(), "HD:out/outfile"];
	
	// some files may be password protected (sample/archive/xpk/G-SpellMoon1.0)
	// Below I tried to use a simple REXX script that will queue up 'password' as the password input and then run our actual bin, xfdDecrunch, thus preventing it from haning waiting for password input
	// Sadly, while running the generated go.rexx script manually works fine on the amiga, it doesn't work when it's run from the supervisor, and I could not figure out why
	// so we just run the xfdDecrunch command directly and will just have to wait for the built in supervisor.rexx 60 second timeout. sigh.
	/*osData = r => ({
		script : [
			`QUEUE "password"`,
			`ADDRESS command xfdDecrunch "HD:in/${r.inFile()}" "HD:out/outfile" "FORCE" "NOASK" "NOXPKPWD"`
		] });*/
	
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
