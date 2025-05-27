import {Format} from "../../Format.js";

export class gemViewMGF extends Format
{
	name        = "GEMView MGF";
	ext         = [".mgf"];
	magic       = ["GEMView MGF"];
	weakMagic   = true;
	unsupported = true;
}
