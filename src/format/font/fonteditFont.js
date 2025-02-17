import {Format} from "../../Format.js";

export class fonteditFont extends Format
{
	name           = "FONTEDIT Font";
	website        = "http://justsolve.archiveteam.org/wiki/FONTEDIT_font";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["FONTEDIT Font"];
	converters     = ["deark[module:fontedit]"];
}
