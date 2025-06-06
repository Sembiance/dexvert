import {Format} from "../../Format.js";

export class amosSpriteBank extends Format
{
	name       = "AMOS Sprite Bank";
	website    = "http://fileformats.archiveteam.org/wiki/AMOS_Sprite_Bank";
	ext        = [".abk"];
	mimeType   = "image/x-amos-spritebank";
	magic      = ["AMOS Basic sprite bank", "AMOS Sprites Bank", "deark: abk (AMOS Sprite Bank)"];
	converters = ["dumpamos"];
}
