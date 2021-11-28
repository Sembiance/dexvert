import {Format} from "../../Format.js";

export class tencentTAP extends Format
{
	name       = "Tencent TAP";
	website    = "http://fileformats.archiveteam.org/wiki/TAP_(Tencent)";
	ext        = [".tap"];
	mimeType   = "image/vnd.tencent.tap";
	magic      = ["TAP (Tencent) bitmap"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
