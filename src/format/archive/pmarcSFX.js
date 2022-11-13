import {Format} from "../../Format.js";

export class pmarcSFX extends Format
{
	name       = "PMarc SFX Archive";
	ext        = [".com"];
	magic      = ["PMarc CP/M SFX archive", "PMarc SFX archive"];
	converters = ["lha"];
}
