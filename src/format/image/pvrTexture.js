import {Format} from "../../Format.js";

export class pvrTexture extends Format
{
	name        = "PVR Texture";
	website     = "https://fabiensanglard.net/Mykaruga/tools/segaPVRFormat.txt";
	ext         = [".pvr"];
	magic       = ["Sega PVR image", "Dreamcast PVR texture format"];
	converters  = ["pvr2png"];
}
