import {Format} from "../../Format.js";

export class keyCAD3DModel extends Format
{
	name           = "keyCAD 3D Model";
	ext            = [".mdl"];
	forbidExtMatch = true;
	magic          = ["KeyCAD Deluxe 3D Model"];
	auxFiles       = (input, otherFiles) =>
	{
		// .fnt files are referenced
		const fntFiles = otherFiles.filter(otherFile => [".fnt"].includes(otherFile.ext.toLowerCase()));
		return fntFiles.length ? fntFiles : false;
	};
	keepFilename = true;
	converters   = ["keyCADDeluxe3D"];
}
