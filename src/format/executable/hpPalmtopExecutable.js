import {Format} from "../../Format.js";

export class hpPalmtopExecutable extends Format
{
	name           = "HP Palmtop Executable";
	ext            = [".exm"];
	forbidExtMatch = true;
	magic          = ["HP Palmtop 95/100/200LX Sys.Manager compliant Executable"];
	weakMagic      = true;
	unsupported    = true;
}
