import {Format} from "../../Format.js";

export class vtf extends Format
{
	name       = "Valve Texture Format";
	website    = "http://fileformats.archiveteam.org/wiki/Valve_Texture_Format";
	ext        = [".vtf"];
	mimeType   = "image/vnd.valve.source.texture";
	magic      = ["Valve Texture Format", /^fmt\/985( |$)/];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
