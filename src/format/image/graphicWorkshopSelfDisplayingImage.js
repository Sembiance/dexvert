import {Format} from "../../Format.js";

export class graphicWorkshopSelfDisplayingImage extends Format
{
	name           = "Graphic Workshop self-displaying image";
	website        = "http://fileformats.archiveteam.org/wiki/Graphic_Workshop_self-displaying_picture";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Graphic Workshop self-displaying picture executable"];
	converters     = ["deark[module:gws_exepic]"];
}
