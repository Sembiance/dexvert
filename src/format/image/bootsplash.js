import {Format} from "../../Format.js";

export class bootsplash extends Format
{
	name         = "Bootsplash Image";
	filename     = [/^bootsplash$/i];
	magic        = ["Bootsplash image", "Bootsplash graphics bitmap"];
	priority     = this.PRIORITY.LOW;
	converters   = ["tomsViewer"];
}
