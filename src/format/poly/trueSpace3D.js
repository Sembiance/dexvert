import {Format} from "../../Format.js";

export class trueSpace3D extends Format
{
	name       = "Caligari TrueSpace 3D Object";
	website    = "http://fileformats.archiveteam.org/wiki/Caligari_trueSpace";
	ext        = [".cob", ".sobj"];
	magic      = ["Caligari TrueSpace data", "Caligari TrueSpace 3D object", /^fmt\/913( |$)/];
	converters = ["assimp", "AccuTrans3D"];
}
