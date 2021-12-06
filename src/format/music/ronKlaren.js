import {Format} from "../../Format.js";

export class ronKlaren extends Format
{
	name         = "Ron Klaren Module";
	ext          = [".rk"];
	magic        = ["Ron Klaren module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
