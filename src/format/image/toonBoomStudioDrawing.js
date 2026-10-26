import {Format} from "../../Format.js";

export class toonBoomStudioDrawing extends Format
{
	name           = "Toon Boom Studio Drawing";
	ext            = [".tbd"];
	forbidExtMatch = true;
	magic          = ["Toon Boom Studio Drawing"];
	converters     = ["vibe2svg"];
}
