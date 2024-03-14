import {Format} from "../../Format.js";

export class openNURBS extends Format
{
	name       = "Rhino OpenNURBS 3D Model";
	website    = "http://fileformats.archiveteam.org/wiki/3DM";
	ext        = [".3dm"];
	magic      = ["Rhinoceros 3D Model", /^x-fmt\/(432|433|434|435)( |$)/];
	converters = ["polyTrans64[format:openNURBS]"];
}
