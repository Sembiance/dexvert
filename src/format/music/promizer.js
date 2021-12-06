import {Format} from "../../Format.js";

export class promizer extends Format
{
	name         = "Promizer Module";
	magic        = [/^Promizer .*module$/];
	metaProvider = ["muscInfo"];
	converters   = ["uade123"];
}
