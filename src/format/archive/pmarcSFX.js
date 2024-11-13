import {Format} from "../../Format.js";

export class pmarcSFX extends Format
{
	name       = "PMarc SFX Archive";
	ext        = [".com"];
	magic      = ["PMarc CP/M SFX archive", "PMarc SFX archive", "PMsfx CP/M self-extracting archive", "16bit COM LHice SFX archive executable"];
	converters = ["lha"];
}
