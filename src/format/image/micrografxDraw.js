import {Format} from "../../Format.js";

export class micrografxDraw extends Format
{
	name           = "Micrografx Draw/Designer";
	website        = "http://fileformats.archiveteam.org/wiki/Micrografx_Draw";
	ext            = [".drw", ".drt", ".ds4", ".dsf"];
	forbidExtMatch = true;
	magic          = ["Micrografx Designer Drawing", "Micrografx Designer Graphics", "RIFF Datei: unbekannter Typ 'MGX '", /^Generic RIFF file MGX $/, "Windows Draw drawing", /^x-fmt\/(47|294|295)( |$)/];
	converters     = [
		// vector
		"scribus",
		"canvas5[vector]",
		
		// raster
		"corelDRAW", "hiJaakExpress", "photoDraw", "corelPhotoPaint", "picturePublisher", "canvas[matchType:magic][nonRaster]"
	];
	verify         = ({meta}) => meta.colorCount>1;
}
