import {Format} from "../../Format.js";

export class freeHandDrawing extends Format
{
	name       = "FreeHand Drawing";
	ext        = [".fh", ".fh2", ".fh3", ".fh4", ".fh5", ".fh6", ".fh7", ".fh8", ".fh9"];
	magic      = ["FreeHand drawing"];
	converters = ["soffice[outType:svg][autoCropSVG]", "scribus"]	// These are often centered on a huge blank canvas, so autoCropSVG will take care of that
}
