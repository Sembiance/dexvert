import {Format} from "../../Format.js";

export class artworxDrawing extends Format
{
	name        = "Artworx Drawing";
	ext         = [".cwg"];
	magic       = ["Artworx drawing"];
	unsupported = true;
}
