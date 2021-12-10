import {Format} from "../../Format.js";

export class pog extends Format
{
	name     = "Print Shop Graphic POG Archive";
	website  = "http://fileformats.archiveteam.org/wiki/The_Print_Shop";
	ext      = [".pog"];
	magic    = ["The Print Shop graphic"];
	auxFiles = (input, otherFiles) =>
	{
		// .pog can convert on it's own, but optionally uses an .pnm
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.pnm`);
		return otherFile ? [otherFile] : false;
	};
	converters = r => [`deark${r.f.aux ? `[file2:${r.f.aux.base}]` : ""}`];
}
