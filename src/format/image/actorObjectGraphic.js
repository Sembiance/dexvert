import {Format} from "../../Format.js";

export class actorObjectGraphic extends Format
{
	name        = "Actor Object Graphic";
	ext         = [".ogl"];
	magic       = ["Actor ObjectGraphics"];
	unsupported = true;	// only 33 unique files on discmaster
}
