import {Format} from "../../Format.js";

export class hiResPlayerMissile extends Format
{
	name       = "HiRes Player Missile";
	ext        = [".hpm"];
	fileSize   = [19203];
	mimeType   = "image/x-hires-player-missile";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
