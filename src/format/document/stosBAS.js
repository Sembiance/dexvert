import {Format} from "../../Format.js";

export class stosBAS extends Format
{
	name           = "Atari STOS Basic";
	website        = "http://fileformats.archiveteam.org/wiki/STOS_memory_bank";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = ["STOS Source"];
	notes          = "I tried using STOSBAS_detokenize.pl and chkbas and both failed. So I just wrote my own.";
	converters     = ["stosBAS2txt"];
}
