import {Format} from "../../Format.js";

export class amigaBASIC extends Format
{
	name           = "AmigaBASIC Source Code";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = [/^AmigaBASIC source$/];
	converters     = ["ab2ascii"];
}
