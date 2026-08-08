import {Format} from "../../Format.js";

export class openNURBS extends Format
{
	name       = "Rhino OpenNURBS 3D Model";
	website    = "http://fileformats.archiveteam.org/wiki/3DM";
	ext        = [".3dm"];
	magic      = ["Rhinoceros 3D Model", /^fmt\/2082( |$)/, /^x-fmt\/(432|433|434|435)( |$)/];
	converters = ["threeDM2GLB"];
}
