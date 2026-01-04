import {xu} from "xu";
import {Format} from "../../Format.js";

export class sounder extends Format
{
	name           = "Sounder";
	ext            = [".snd"];
	forbidExtMatch = [".snd"];
	magic          = [/^soxi: sndr$/];
	weakMagic      = true;
	metaProvider   = ["soxi"];
	converters     = ["sox[type:sndr]"];
	verify         = ({meta}) => meta.duration<xu.HOUR*3;	// some mis-matches in the wild that are 3+ hours long. unlikely to find an actual 3+ hour long sounder format file
}
