import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {path} from "std";
import {fileUtil, runUtil} from "xutil";

export class hfsexplorer extends Program
{
	website = "https://github.com/unsound/hfsexplorer";
	bin     = Program.binPath("hfsexplorer/dist/bin/unhfs");
	flags   = {
		partition : "Which partition to extract. Default: 0"
	};
	args       = r => ["-o",  r.outDir({absolute : true}), "-resforks", "APPLEDOUBLE", "-partition", (r.flags.partition || 0).toString(), r.inFile({absolute : true})];
	runOptions = ({cwd : Program.binPath("hfsexplorer/dist")});
	postExec   = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		await fileUtil.unlink(path.join(path.dirname(outDirPath), "._dexvert_mac"));

		const region = RUNTIME.globalFlags?.osHint?.macintoshjp ? "japan" : "roman";

		r.meta.fileMeta = {};
		const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true, relative : true});
		await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const filename = path.basename(fileOutputPath);
			if(!filename.startsWith("._"))	//, regex : /(^|\/)\._[^/]+$/
				return;

			const originalFilename = filename.substring(2);
			const fullFilePath = path.join(outDirPath, fileOutputPath);
			const originalFilePath = path.join(path.dirname(fullFilePath), originalFilename);

			const originalStat = await xu.tryFallbackAsync(async () => await Deno.stat(originalFilePath));
			if(!originalStat)
				return;

			if(originalStat.isDirectory)
				return await fileUtil.unlink(fullFilePath);

			const rsrcFilePath = path.join(path.dirname(fullFilePath), `${originalFilename}.rsrc`);
			await Deno.rename(fullFilePath, rsrcFilePath);
			const {stdout} = await runUtil.run("deno", runUtil.denoArgs(Program.binPath("appleDouble2MacBinary2.js"), `--originalFilePath=${originalFilePath}`, `--region=${region}`, rsrcFilePath), runUtil.denoRunOpts());
			
			const typeCreator = xu.parseJSON(stdout, {});
			if(typeCreator.macFileType && typeCreator.macFileCreator)
				r.meta.fileMeta[path.relative(outDirPath, originalFilePath)] = typeCreator;
		}, 6);

		if(Object.keys(r.meta.fileMeta).length===0)
			delete r.meta.fileMeta;
	};
	renameOut = false;
}
