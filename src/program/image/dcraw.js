import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class dcraw extends Program
{
	website  = "https://www.cybercom.net/~dcoffin/dcraw/";
	package  = "media-gfx/dcraw";
	bin      = "dcraw";
	args     = r => [r.inFile()];
	postExec = async r =>
	{
		const ppmFilePaths = await fileUtil.tree(r.f.root, {regex : /\.ppm$/, nodir : true});
		await ppmFilePaths.parallelMap(async ppmFilePath => await fileUtil.move(ppmFilePath, path.join(r.outDir({absolute : true}), path.basename(ppmFilePath))));
	};
	chain = "convert";
}
