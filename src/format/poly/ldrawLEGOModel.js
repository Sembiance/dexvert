import {Format} from "../../Format.js";

export class ldrawLEGOModel extends Format
{
	name           = "LDraw LEGO Model";
	website        = "http://www.ldraw.org/";
	ext            = [".ldr", ".dat"];
	forbidExtMatch = [".dat"];
	magic          = ["LDraw Model"];
	converters     = ["threeDObjectConverter"];
	notes          = "Another converter, blender plugin I could use: https://github.com/trevorsandy/blenderldrawrender";
}
