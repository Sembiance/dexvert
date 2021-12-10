import {Format} from "../../Format.js";

export class setupMVA extends Format
{
	name        = "Setup Program Archive";
	ext         = [".mva"];
	magic       = ["Setup Program Archive"];
	unsupported = true;
}
