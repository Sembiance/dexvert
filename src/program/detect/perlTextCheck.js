import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil, runUtil} from "xutil";

export class perlTextCheck extends Program
{
	website = "https://www.perl.org";
	package = "dev-lang/perl";
	bin     = "perl";
	loc     = "local";
	
	// text files sometimes have trailing 0x00 and 0x1A bytes, while the rest is all text
	// we trim those off first and pass that output to perl to check to see if what's left is likely text or not
	// we include the --newlines flag because sometimes the 0x00 and 0x01A bytes are interspersed with trailing \n and \r characters
	pre = async r =>
	{
		r.trimmedFilePath = await fileUtil.genTempPath();
		await runUtil.run(Program.binPath("trimGarbage/trimGarbage"), ["--newlines", r.inFile({absolute : true}), r.trimmedFilePath]);
		if(!(await fileUtil.exists(r.trimmedFilePath)))
			delete r.trimmedFilePath;
	};
	args = r => ["-le", `print -B $ARGV[0] ? "" : "Likely Text (Perl)"`, "--", r.trimmedFilePath || r.inFile()];
	post = async r =>
	{
		if(r.trimmedFilePath)
			await fileUtil.unlink(r.trimmedFilePath);
		r.meta.detections = r.stdout.trim().split("\n").filter(v => !!v).map(line => Detection.create({value : line.trim(), from : "perlTextCheck", file : r.f.input}));
	};
	renameOut = false;
}
