import {Format} from "../../Format.js";

export class xps extends Format
{
	name       = "Open XML Paper Specification";
	website    = "http://fileformats.archiveteam.org/wiki/XPS";
	ext        = [".xps", ".oxps"];
	mimeType   = "application/oxps";
	magic      = ["Open XML Paper Specification", /^fmt\/(189|657)( |$)/];
	converters = ["xpstopdf", `abydosconvert[format:${this.mimeType}]`];
}
