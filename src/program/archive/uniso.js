import {Program} from "../../Program.js";

export class uniso extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	flags   = {
		offset : "Extract ISO starting at this particular byte offset. Default: 0",
		hfs    : "Set this to true to process the iso as a MacOS HFS disc. Default: false"
	};
	bin        = "deno";
	args       = r =>
	{
		const a = [];
		if(r.flags.offset)
			a.push(`--offset=${r.flags.offset}`);
		if(r.flags.hfs)
			a.push("--hfs");
		a.push(r.inFile(), r.outDir());
		return Program.denoArgs(Program.binPath("uniso.js"), ...a);
	};
	runOptions = ({env : Program.denoEnv()});
	renameOut  = false;
}
