import {Format} from "../../Format.js";

export class madeSoundFile extends Format
{
	name           = "MADE Sound File";
	ext            = [".sfl"];
	forbidExtMatch = true;
	magic          = ["MADE Sound File"];
	converters     = ["vibe2wav[renameOut]"];
}
