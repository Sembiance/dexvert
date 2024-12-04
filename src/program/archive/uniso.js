import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";

export class uniso extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	package = "sys-fs/hfsutils";
	flags   = {
		offset     : "Extract ISO starting at this particular byte offset. Default: 0",
		block      : "Specify the block size in bytes",
		hfs        : "Set this to true to process the iso as a MacOS HFS disc. Default: false",
		hfsplus    : "Set this to true to process the iso as a MacOS HFS+ disc. Default: false",
		nextstep   : "Set this to true to process the iso as a NeXTSTEP disc. Default: false",
		type       : "Specify the type of filesystem to extract.",
		options    : "Additional options to pass to the mount command",
		checkMount : "Set to true to check the mount for any input/output errors and abort if there are any"
	};
	bin  = "deno";
	args = r =>
	{
		const a = ["--ts", r.f.input.ts];
		if(r.flags.offset)
			a.push(`--offset=${r.flags.offset}`);
		if(r.flags.block)
			a.push(`--block=${r.flags.block}`);
		if(r.flags.hfs)
		{
			a.push("--hfs");
			a.push(`--macEncoding=${RUNTIME.globalFlags?.osHint?.macintoshjp ? "japan" : "roman"}`);
		}
		if(r.flags.hfsplus)
			a.push("--hfsplus");
		if(r.flags.nextstep)
			a.push("--nextstep");
		if(r.flags.checkMount)
			a.push("--checkMount");
		if(r.flags.type)
			a.push(`--type=${r.flags.type}`);
		if(r.flags.options)
			a.push(`--options=${r.flags.options}`);
		a.push(r.inFile(), r.outDir());
		return Program.denoArgs(Program.binPath("uniso.js"), ...a);
	};
	runOptions = ({env : Program.denoEnv()});
	post       = r =>
	{
		const meta = xu.parseJSON(r.stdout, {});
		if(r.flags?.subOutDir && meta.fileMeta)
			meta.fileMeta = Object.fromEntries(Object.entries(meta.fileMeta).map(([k, v]) => [`${r.flags.subOutDir}/${k}`, v]));

		return Object.assign(r.meta, meta);
	};
	renameOut = false;
}
