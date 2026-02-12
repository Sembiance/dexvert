import {Format} from "../../Format.js";

export class pvrTexture extends Format
{
	name        = "PVR Texture";
	website     = "http://fileformats.archiveteam.org/wiki/PVR_Texture";
	ext         = [".pvr"];
	magic       = ["Sega PVR image", "Dreamcast PVR texture format", "PowerVR Image texture format", /^geViewer: PVM_PVMH_PVR_PVRT( |$)/];
	converters  = ["pvr2png", "gameextractor[renameOut][codes:PVM_PVMH_PVR_PVRT]", "noesis[type:image][hasExtMatch][matchType:magic]"];
}
