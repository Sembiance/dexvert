import {Format} from "../../Format.js";

export class pvrTexture extends Format
{
	name        = "PVR Texture";
	website     = "http://fileformats.archiveteam.org/wiki/PVR_Texture";
	ext         = [".pvr"];
	magic       = ["Sega PVR image", "Dreamcast PVR texture format", "PowerVR Image texture format"];
	converters  = ["pvr2png", "noesis[type:image]"];
}
