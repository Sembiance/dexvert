import {Format} from "../../Format.js";

export class faceTheMusic extends Format
{
	name           = "Face The Music Module";
	website        = "http://eab.abime.net/showthread.php?t=62254";
	ext            = [".ftm"];
	forbidExtMatch = true;
	magic          = ["FaceTheMusic module", "Face The Music module"];
	metaProvider   = ["musicInfo"];
	converters     = ["openmpt123"]
}
