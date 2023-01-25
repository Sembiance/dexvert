import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";

export class fuseiso extends Program
{
	website = "https://sourceforge.net/projects/fuseiso";
	package = "sys-fs/fuseiso";
	flags   = {
		excludeVCD : "If set to true, this is a VCD and we should exclude VCD files as they handled by vcdxrip"
	};
	bin     = "fuseiso";
	args    = async r =>
	{
		r.fuseISOMountDirPath = await fileUtil.genTempPath(r.f.root, "_fuseiso");
		await Deno.mkdir(r.fuseISOMountDirPath);

		return [r.inFile(), r.fuseISOMountDirPath];
	};
	postExec = async r =>
	{
		await runUtil.run("rsync", ["-sa", ...(r.flags.excludeVCD ? ["cdi", "ext", "mpegav", "vcd"].flatMap(v => ([`--exclude=/${v}/`, `--exclude=/${v.toUpperCase()}/`])) : []), `${r.fuseISOMountDirPath}/`, `${r.outDir({absolute : true})}/`]);
		await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
	};
	renameOut = false;
}
