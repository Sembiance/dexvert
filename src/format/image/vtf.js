import {Format} from "../../Format.js";

export class vtf extends Format
{
	name       = "Valve Texture Format";
	website    = "http://fileformats.archiveteam.org/wiki/Valve_Texture_Format";
	ext        = [".vtf"];
	mimeType   = "image/vnd.valve.source.texture";
	magic      = ["Valve Texture Format", "Format: Valve Texture", /^geViewer: VTF_VTF( |$)/, /^fmt\/985( |$)/];
	converters = ["gameextractor[renameOut][codes:VTF_VTF]", `abydosconvert[format:${this.mimeType}]`, "noesis[type:image]"];
}
