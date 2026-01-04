import {Format} from "../../Format.js";

export class yamahaTX extends Format
{
	name         = "Yamaha TX Wave Sample";
	ext          = [".txw"];
	magic        = ["Yamaha TX Wave", "Yamaha TX-16W samples audio", /^soxi: txw$/, /^fmt\/(1661|1662)( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox[type:txw]", "awaveStudio[matchType:magic]"];
}
