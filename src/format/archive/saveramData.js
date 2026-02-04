import {Format} from "../../Format.js";

export class saveramData extends Format
{
	name           = "SAVERAM Data";
	ext            = [".fls", ".ram"];
	forbidExtMatch = true;
	magic          = ["SAVERAM Data", "SaveRam2 compressed data"];
	converters     = ["loadram"];
}
