import {Format} from "../../Format.js";

export class micrografxDraw extends Format
{
	name           = "Micrografx Draw/Designer";
	website        = "http://fileformats.archiveteam.org/wiki/Micrografx_Draw";
	ext            = [".drw", ".drt", ".ds4", ".dsf"];
	forbidExtMatch = true;
	magic          = ["Micrografx Designer Drawing", "Micrografx Designer Graphics", /^x-fmt\/(294|295)( |$)/];
	converters     = ["scribus", "corelDRAW", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas[matchType:magic][nonRaster]"];
	verify         = ({meta}) => meta.colorCount>1;
}
