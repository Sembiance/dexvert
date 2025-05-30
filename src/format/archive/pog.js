import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class pog extends Format
{
	name     = "Print Shop Graphic POG Archive";
	website  = "http://fileformats.archiveteam.org/wiki/The_Print_Shop";
	ext      = [".pog"];
	magic    = ["The Print Shop graphic", "deark: newprintshop (The New Print Shop (POG/PNM))"];
	idCheck = async inputFile => inputFile.size>4 && (await fileUtil.readFileBytes(inputFile.absolute, 4))[3]===0x01;
	auxFiles = (input, otherFiles) =>
	{
		// .pog can convert on it's own, but optionally uses an .pnm
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.pnm`);
		return otherFile ? [otherFile] : false;
	};
	converters = dexState => [`deark[module:newprintshop]${dexState.f.aux ? `[file2:${dexState.f.aux.base}]` : ""}`];
}
