import {Format} from "../../Format.js";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class svg extends Format
{
	name      = "Scalable Vector Graphics";
	website   = "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics";
	ext       = [".svg", ".svgz"];
	mimeType  = "image/svg+xml";
	magic     = ["SVG Scalable Vector Graphics image"];
	untouched = dexState => dexState.meta.width && dexState.meta.height;

	meta = async inputFile =>
	{
		const svgInfoR = await Program.runProgram("svgInfo", inputFile);
		await fileUtil.unlink(svgInfoR.f.outDir.absolute, {recursive : true});
		await fileUtil.unlink(svgInfoR.f.homeDir.absolute, {recursive : true});
		return svgInfoR.meta;
	};
}
