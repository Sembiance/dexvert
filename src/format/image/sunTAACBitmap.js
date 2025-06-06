import {Format} from "../../Format.js";

export class sunTAACBitmap extends Format
{
	name           = "Sun TAAC Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Sun_TAAC_image";
	ext            = [".iff", ".vff", ".suniff", "taac"];
	forbidExtMatch = true;
	magic          = ["Sun TAAC bitmap", "Sun TAAC Image :taac:"];
	weakMagic      = true;
	converters     = ["imconv[format:iff]", "nconvert[format:taac]"];
}
