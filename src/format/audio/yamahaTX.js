import {Format} from "../../Format.js";

export class yamahaTX extends Format
{
	name         = "Yamaha TX Wave Sample";
	ext          = [".txw"];
	magic        = [" Yamaha TX Wave", "Yamaha TX-16W samples audio"];
	metaProvider = ["soxi"];
	converters   = ["sox", "awaveStudio"];
}
