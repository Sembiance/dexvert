import {Format} from "../../Format.js";

export class makeread extends Format
{
	name           = "makeread COM File";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = [/^deark: makeread$/];
	converters     = ["deark[module:makeread][opt:text:encconv=0]"];
}
