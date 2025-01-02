import {Format} from "../../Format.js";

export class psionVoice extends Format
{
	name         = "Psion Voice";
	ext          = [".prc"];
	magic        = ["Psion Series 5 voice note", "Psion Record/EPOC voice audio", /^soxi: prc$/, /^Psion Series 5 Record file voice note/];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
