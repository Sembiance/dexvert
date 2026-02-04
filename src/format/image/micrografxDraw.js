import {Format} from "../../Format.js";

export class micrografxDraw extends Format
{
	name    = "Micrografx Draw/Designer";
	website = "http://fileformats.archiveteam.org/wiki/Micrografx_Draw";
	
	// .mgx not yet supported, so we explicitly don't include it so hasExtMatch below for canvas doesn't match and convert to just an garbage output
	// don't put .grf in here because then scribus fails to handle the file
	ext = [".drw", ".drt", ".ds4", ".dsf"];

	forbidExtMatch = true;
	magic          = ["Micrografx Designer Drawing", "Micrografx Designer Graphics", "RIFF Datei: unbekannter Typ 'MGX '", /^Generic RIFF file MGX$/, "Windows Draw drawing", /^x-fmt\/(47|294|295)( |$)/];
	converters     = [
		// vector
		"scribus",
		"canvas5[vector]",
		
		// raster
		"corelDRAW", "hiJaakExpress", "photoDraw", "corelPhotoPaint", "picturePublisher", "canvas[matchType:magic][nonRaster][hasExtMatch]"
	];
	verify         = ({meta}) => meta.colorCount>1;
}
