import {Format} from "../../Format.js";

export class printMasterShape extends Format
{
	name           = "PrintMaster Shape";
	website        = "http://fileformats.archiveteam.org/wiki/PrintMaster";
	ext            = [".shp"];
	forbidExtMatch = true;
	magic          = ["Printmaster Shape bitmap", "deark: printmaster (PrintMaster (SHP/SDR))"];
	auxFiles       = (input, otherFiles) =>
	{
		// .shp can convert on it's own, but optionally uses an .sdr
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.sdr`);
		return otherFile ? [otherFile] : false;
	};
	converters = r => [`deark[module:printmaster]${r.f.aux ? `[file2:${r.f.aux.base}]` : ""}`];
}
