import {Format} from "../../Format.js";

export class teletextPackets extends Format
{
	name           = "Teletext Packets";
	ext            = [".t42"];
	mimeType       = "text/x-t42-packets";
	forbiddenMagic = ["Kopftext: 'T42FONT'"];
	priority       = this.PRIORITY.LOW;
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}
