import {Format} from "../../Format.js";

export class prismPaint extends Format
{
	name           = "Prism Paint";
	website        = "http://fileformats.archiveteam.org/wiki/Prism_Paint";
	ext            = [".pnt", ".tpi"];
	forbidExtMatch = [".pnt"];	// .pnt is so common an extension and the magic is pretty robust
	mimeType       = "image/x-prism-paint";
	magic          = ["Prism Paint bitmap"];
	//priority       = this.PRIORITY.LOW;
	converters     = ["deark", "recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
