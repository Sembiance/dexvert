import {Format} from "../../Format.js";

export class btoaEncoded extends Format
{
	name           = "BTOA Encoded";
	website        = "http://fileformats.archiveteam.org/wiki/Ascii85";
	ext            = [".ab"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["btoa encoded data", /^btoa'd/];
	converters     = ["ascii85Decoder"];
}
