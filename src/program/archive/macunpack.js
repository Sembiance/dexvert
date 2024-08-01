import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil, encodeUtil} from "xutil";

export class macunpack extends Program
{
	website  = "https://github.com/wnayes/macutils";
	package  = "app-arch/macutils";
	bin      = "macunpack";
	unsafe   = true;
	args     = r => [r.inFile()];
	cwd      = r => r.outDir();
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		const foldernameFilepaths = await fileUtil.tree(outDirPath, {nodir : true, sort : true, regex : /\.foldername$/});
		for(const foldernameFilepath of foldernameFilepaths.reverse())
		{
			const data = (await Deno.readFile(foldernameFilepath)).subarray(2);
			await fileUtil.unlink(foldernameFilepath);
			await Deno.rename(path.dirname(foldernameFilepath), path.join(path.dirname(path.dirname(foldernameFilepath)), await encodeUtil.decodeMacintosh({data, skipNullBytes : true})));
		}
	};
	renameOut = false;
}
