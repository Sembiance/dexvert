import {Format} from "../../Format.js";
import {Program} from "../../Program.js";

export class svg extends Format
{
	name           = "Scalable Vector Graphics";
	website        = "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics";
	ext            = [".svg", ".svgz"];
	forbidExtMatch = true;
	mimeType       = "image/svg+xml";
	magic          = ["SVG Scalable Vector Graphics image", "Scalable Vector Graphics", "SVG XML document", /^fmt\/(91|92|413)( |$)/];
	untouched      = dexState => dexState.meta.width && dexState.meta.height;
	meta           = async (inputFile, dexState) => (await Program.runProgram("svgInfo", inputFile, {xlog : dexState.xlog, autoUnlink : true})).meta;
}
