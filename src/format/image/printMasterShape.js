import {Format} from "../../Format.js";

export class printMasterShape extends Format
{
	name           = "PrintMaster Shape";
	website        = "http://fileformats.archiveteam.org/wiki/PrintMaster";
	magic          = ["Printmaster Shape bitmap"];
	ext            = [".shp"];
	forbidExtMatch = true;
	auxFiles       = (input, otherFiles) =>
	{
		// .neo can convert on it's own, but optionally uses an .rst
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.sdr`);
		return otherFile ? [otherFile] : false;
	};
	converters = r => [`deark[module:printmaster]${r.f.aux ? `[file2:${r.f.aux.base}]` : ""}`];
}
