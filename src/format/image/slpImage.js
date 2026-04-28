import {Format} from "../../Format.js";

export class slpImage extends Format
{
	name           = "SLP Image";
	website        = "http://fileformats.archiveteam.org/wiki/Age_of_Empires_Graphics_File";
	ext            = [".slp"];
	forbidExtMatch = true;
	magic          = ["SLP Image", "Age of Empires Graphics"];
	converters     = ["vibe2png"];
}
