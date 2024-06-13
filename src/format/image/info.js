import {Format} from "../../Format.js";

export class info extends Format
{
	name       = "Amiga Workbench Icon";
	website    = "http://fileformats.archiveteam.org/wiki/Amiga_Workbench_icon";
	ext        = [".info"];
	magic      = [/^Amiga Workbench.* icon/, "Amiga Workbench project icon"];
	mimeType   = "image/x-amiga-icon";
	converters = ["deark[module:amigaicon]", `abydosconvert[format:${this.mimeType}]`, "paintDotNet"];
}
