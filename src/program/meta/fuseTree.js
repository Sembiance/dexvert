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
	post = async r =>
	{
		const {stderr} = await runUtil.run("ls", [r.fuseISOMountDirPath]);
		if(stderr.trim().length===0)
		{
			r.meta.tree = ((await fileUtil.tree(r.fuseISOMountDirPath)) || []).map(v => path.relative(r.fuseISOMountDirPath, v));
			if(!r.meta.tree?.length)
				delete r.meta.tree;
		}
		await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
	};
	renameOut = false;
}
