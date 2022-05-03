import {Format} from "../../Format.js";

export class openNURBS extends Format
{
	name        = "OpenNURBS 3D Model";
	website     = "http://fileformats.archiveteam.org/wiki/3DM";
	ext         = [".3dm"];
	magic       = ["Rhinoceros 3D Model"];
	unsupported = true;
}
