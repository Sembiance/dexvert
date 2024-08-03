import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";

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
		r.xlog.debug`retrieving 'ls -R' output from fuseiso mounted ISO as a test to see if it mounted correctly...`;

		let stderrDataExists = false;
		const stderrcb = (line, p) =>
		{
			if(stderrDataExists || !line?.trim()?.length)
				return;

			stderrDataExists = true;
			runUtil.kill(p);
		};
		const {status} = await runUtil.run("ls", ["-R", r.fuseISOMountDirPath], {stdoutNull : true, stderrcb, timeout : xu.SECOND*8});
		r.xlog.debug`'ls -R' result: ${{status, stderrDataExists}}`;

		if(stderrDataExists)
		{
			r.xlog.debug`fuseiso mount point ${r.fuseISOMountDirPath} did not mount correctly, unmounting...`;
			await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
			await fileUtil.unlink(r.fuseISOMountDirPath, {recursive : true});
			delete r.fuseISOMountDirPath;
		}
	};
	post = async r =>
	{
		if(!r.fuseISOMountDirPath)
			return;

		r.xlog.debug`retrieving file tree of fuseiso mount point ${r.fuseISOMountDirPath}...`;
		r.meta.tree = ((await fileUtil.tree(r.fuseISOMountDirPath, {relative : true, depth : 3})) || []);
		if(!r.meta.tree?.length)
			delete r.meta.tree;

		await runUtil.run("fusermount", ["-u", r.fuseISOMountDirPath]);
		await fileUtil.unlink(r.fuseISOMountDirPath, {recursive : true});
	};
	renameOut = false;
}
