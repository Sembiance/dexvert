import {Format} from "../../Format.js";
import {Program} from "../../Program.js";

export class svg extends Format
{
	name      = "Scalable Vector Graphics";
	website   = "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics";
	ext       = [".svg", ".svgz"];
	mimeType  = "image/svg+xml";
	magic     = ["SVG Scalable Vector Graphics image"];
	untouched = dexState => dexState.meta.width && dexState.meta.height;

	meta = async (inputFile, xlog) =>
	{
		const svgInfoR = await Program.runProgram("svgInfo", inputFile, {xlog});
		await svgInfoR.unlinkHomeOut();
		return svgInfoR.meta;
	};
}
