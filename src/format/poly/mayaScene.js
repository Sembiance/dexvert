import {Format} from "../../Format.js";

export class mayaScene extends Format
{
	name        = "Maya Scene";
	website     = "http://fileformats.archiveteam.org/wiki/Maya_scene";
	ext         = [".mb", ".ma"];
	magic       = ["Maya Binary Scene", "Alias Maya Binary File", "Alias Maya Ascii File", "Maya ASCII Scene", /^fmt\/(861|862|863)( |$)/];
	unsupported = true;
}
