import {Format} from "../../Format.js";

export class spinBakerSBX extends Format
{
	name           = "SpinBaker SBX Archive";
	ext            = [".sb"];
	forbidExtMatch = true;
	magic          = ["SBX SpinnerBaker eXtractor compressed archive", "SBX Archiv gefunden", /^SBX archive data/];
	converters     = ["spinBakerSBX"];
}
