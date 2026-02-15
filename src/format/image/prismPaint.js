import {Format} from "../../Format.js";

export class prismPaint extends Format
{
	name           = "Prism Paint";
	website        = "http://fileformats.archiveteam.org/wiki/Prism_Paint";
	ext            = [".pnt", ".tpi"];
	forbidExtMatch = [".pnt"];	// .pnt is so common an extension and the magic is pretty robust
	mimeType       = "image/x-prism-paint";
	magic          = ["Prism Paint bitmap", "deark: prismpaint", /^fmt\/1732( |$)/];
	//priority       = this.PRIORITY.LOW;
	converters     = ["deark[module:prismpaint]", "recoil2png[format:PNT.FalconPnt,TPI]", `abydosconvert[format:${this.mimeType}]`];
}
