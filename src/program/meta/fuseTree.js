import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

export class fuseTree extends Program
{
	website = "https://sourceforge.net/projects/fuseiso";
	package = "sys-fs/fuseiso";
	bin     = "fuseiso";
	args    = async r =>
	{
		r.fuseISOMountDirPath = await fileUtil.genTempPath(r.f.root, "_fuseiso");
		await Deno.mkdir(r.fuseISOMountDirPath);
		return [r.inFile(), r.fuseISOMountDirPath];
	};
	postExec = async r =>
	{
		const {stderr} = await runUtil.run("ls", ["-R", r.fuseISOMountDirPath]);
		if(!stderr.toLowerCase().includes("input/output error"))
			return;
		
		await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
		await fileUtil.unlink(r.fuseISOMountDirPath, {recursive : true});
		delete r.fuseISOMountDirPath;
	};
	post = async r =>
	{
		if(!r.fuseISOMountDirPath)
			return;

		r.meta.tree = ((await fileUtil.tree(r.fuseISOMountDirPath)) || []).map(v => path.relative(r.fuseISOMountDirPath, v));
		if(!r.meta.tree?.length)
			delete r.meta.tree;

		await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
		await fileUtil.unlink(r.fuseISOMountDirPath, {recursive : true});
	};
	renameOut = false;
}
