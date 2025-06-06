import {Format} from "../../Format.js";

export class casioQVCAM extends Format
{
	name       = "Casio QV CAMera Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Casio_CAM";
	ext        = [".cam"];
	magic      = ["Casio QV digital CAMera bitmap", "QV-10 Camera :cam:", "QV-5000sx Camera :cam:", /^fmt\/1772( |$)/];
	converters = ["nconvert[format:cam]"];
}
