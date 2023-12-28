import {Format} from "../../Format.js";

export class hiResPlayerMissile extends Format
{
	name       = "HiRes Player Missile";
	website    = "http://fileformats.archiveteam.org/wiki/HiRes_Player_Missile";
	ext        = [".hpm"];
	fileSize   = [19203];
	mimeType   = "image/x-hires-player-missile";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
