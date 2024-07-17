import {Format} from "../../Format.js";

export class trueSpace3D extends Format
{
	name       = "Caligari TrueSpace 3D Object";
	website    = "http://fileformats.archiveteam.org/wiki/Caligari_trueSpace";
	ext        = [".cob", ".sobj"];
	magic      = ["Caligari TrueSpace", /^fmt\/(913|914)( |$)/];
	converters = ["assimp", "AccuTrans3D", "polyTrans64[format:trueSpace3D]"];	// threeDObjectConverter also claims support but does VERY poorly
}
