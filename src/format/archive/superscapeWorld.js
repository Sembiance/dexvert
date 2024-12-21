import {Format} from "../../Format.js";

export class superscapeWorld extends Format
{
	name       = "Superscape World";
	website    = "https://archive.superscape.org/About%20Superscape.txt";
	ext        = [".vrt", ".xvr", ".svr"];
	magic      = [/^Superscape (VRT|XVR|SVR)$/];
	converters = ["superscapeVRT"];
}
