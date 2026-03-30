import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil, runUtil} from "xutil";

export class guideml extends Program
{
	website  = "http://aminet.net/package/text/hyper/guideml";
	unsafe   = true;
	bin      = "vamos";
	args     = r => [...Program.vamosArgs("GuideML_OS3"), "FILE", r.inFile(), "TO", path.join(r.outDir(), "/")];
	osData   = ({noAuxFiles : true});
	postExec = async r =>
	{
		const fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}));
		const mainFilePath = fileOutputPaths.find(fileOutputPath => path.basename(fileOutputPath).toLowerCase()==="main.html");
		if(!mainFilePath)
			return;

		const outputFilePath = await r.outFile(`${r.originalInput.base}.html`, {absolute : true});
		await runUtil.run("python3", [Program.binPath("amigaGuideCombine.py"), mainFilePath, outputFilePath]);
		if(await fileUtil.exists(outputFilePath))
			await fileOutputPaths.parallelMap(async fileOutputPath => await fileUtil.unlink(fileOutputPath));
	};
	renameOut = false;
}
