import {Format} from "../../Format.js";

export class cmx extends Format
{
	name           = "Corel Metafile Exchange Image";
	website        = "http://fileformats.archiveteam.org/wiki/CMX";
	ext            = [".cmx"];
	forbidExtMatch = true;
	magic          = ["Corel Metafile Exchange Image", "Corel Presentation Exchange File", "RIFF Datei: unbekannter Typ 'CMX1'", "Generic RIFF file CMX1", "deark: riff (Corel CMX)", "Corel Metafile Exchange :cmx:", /^x-fmt\/34( |$)/, /^x-fmt\/35( |$)/];
	converters     = [
		"soffice[outType:svg]", "uniconvertor[autoCrop]", "deark[module:corel_ccx]",
		"hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas[matchType:magic][nonRaster]", "nconvert[format:cmx]"
	];
}
