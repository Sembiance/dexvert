import {Format} from "../../Format.js";

export class casioQVCAM extends Format
{
	name       = "Casio QV CAMera Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Casio_CAM";
	ext        = [".cam"];
	magic      = ["Casio QV digital CAMera bitmap", /^fmt\/1772( |$)/];
	converters = ["nconvert"];
}
