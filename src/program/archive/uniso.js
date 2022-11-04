import {Program} from "../../Program.js";

export class uniso extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	flags   = {
		offset     : "Extract ISO starting at this particular byte offset. Default: 0",
		block      : "Specify the block size in bytes",
		hfs        : "Set this to true to process the iso as a MacOS HFS disc. Default: false",
		nextstep   : "Set this to true to process the iso as a NeXTSTEP disc. Default: false",
		checkMount : "Set to true to check the mount for any input/output errors and abort if there are any"
	};
	bin        = "deno";
	args       = r =>
	{
		const a = ["--ts", r.f.input.ts];
		if(r.flags.offset)
			a.push(`--offset=${r.flags.offset}`);
		if(r.flags.block)
			a.push(`--block=${r.flags.block}`);
		if(r.flags.hfs)
			a.push("--hfs");
		if(r.flags.nextstep)
			a.push("--nextstep");
		if(r.flags.checkMount)
			a.push("--checkMount");
		a.push(r.inFile(), r.outDir());
		return Program.denoArgs(Program.binPath("uniso.js"), ...a);
	};
	runOptions = ({env : Program.denoEnv()});
	renameOut  = false;
}
