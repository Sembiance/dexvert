import {Format} from "../../Format.js";

export class actionamics extends Format
{
	name         = "Actionamics Sound Tool Module";
	ext          = [".ast"];
	magic        = ["Actionamics Sound Tool module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

