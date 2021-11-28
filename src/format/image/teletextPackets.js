import {Format} from "../../Format.js";

export class teletextPackets extends Format
{
	name       = "Teletext Packets";
	ext        = [".t42"];
	mimeType   = "text/x-t42-packets";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
