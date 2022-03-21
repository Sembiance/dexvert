import {Format} from "../../Format.js";

export class micrografxDraw extends Format
{
	name           = "Micrografx Draw/Designer";
	website        = "http://fileformats.archiveteam.org/wiki/Micrografx_Draw";
	ext            = [".drw", ".drt", ".ds4", ".dsf"];
	forbidExtMatch = true;
	magic          = ["Micrografx Designer Drawing"];
	converters     = ["scribus", "hiJaakExpress"];
}
