import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

export class fuseTree extends Program
{
	website    = "https://sourceforge.net/projects/fuseiso";
	package    = "sys-fs/fuseiso";
	bin        = "fuseiso";
	runOptions = ({timeout : xu.SECOND*30});
	args       = async r =>
	{
		r.fuseISOMountDirPath = await fileUtil.genTempPath(r.f.root, "_fuseiso");
		await Deno.mkdir(r.fuseISOMountDirPath);
		return [r.inFile(), r.fuseISOMountDirPath];
	};
	postExec = async r =>
	{
		const {stderr} = await runUtil.run("ls", ["-R", r.fuseISOMountDirPath], {timeout : xu.SECOND*10});
		if(stderr?.length)
		{
			await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
			await fileUtil.unlink(r.fuseISOMountDirPath, {recursive : true});
			delete r.fuseISOMountDirPath;
		}
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
