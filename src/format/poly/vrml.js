import {Format} from "../../Format.js";

export class vrml extends Format
{
	name        = "Virtual Reality Modeling Language";
	website     = "http://fileformats.archiveteam.org/wiki/VRML";
	ext         = [".wrl", ".wrz"];
	magic       = ["Virtual Reality Modeling Language", "ISO/IEC 14772 VRML 97 file", /^fmt\/94( |$)/];
	unsupported = true;
	notes       = "A 3D rendering file format meant for the web.";
}
