import {Format} from "../../Format.js";

export class quartetPSG extends Format
{
	name         = "Quartet PSG Module";
	ext          = [".sqt"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
