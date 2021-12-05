import {Format} from "../../Format.js";

export class accessDatabase extends Format
{
	name       = "Microsoft Access Database";
	ext        = [".mdb"];
	magic      = ["Microsoft Access Database", "Microsoft Jet DB"];
	converters = ["unmdb"];
}
