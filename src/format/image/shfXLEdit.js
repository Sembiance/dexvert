import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";

export class shfXLEdit extends Format
{
	name        = "SHF-XL Edit";
	ext         = [".shx", ".shf"];
	idCheck     = () => RUNTIME.globalFlags?.osHint?.commodore;	// no magic match, so only match if we have explicitly set an environment variable as commodore
	converters  = ["recoil2png[format:SHF,SHX]"];
}
