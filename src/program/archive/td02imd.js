import {Program} from "../../Program.js";

export class td02imd extends Program
{
	website = "http://dunfield.classiccmp.org/img42841/teledisk.htm";
	package = "app-arch/td02imd";
	unsafe  = true;
	bin     = "td02imd";
	args    = async r => [r.inFile(), `O=${await r.outFile("out.imd")}`];
	post    = r =>
	{
		const comment = r.stdout.trim().split("\n").filter(line =>
		{
			if(line.startsWith("TD 1.5"))
				return false;
			
			if(line.endsWith(" sectors converted."))
				return false;
			
			return true;
		}).join("\n");
		if(comment.trim().length)
			r.meta.comment = comment;
	};
	renameOut = false;
	chain     = "dexvert[asFormat:archive/imageDisk]";
}
