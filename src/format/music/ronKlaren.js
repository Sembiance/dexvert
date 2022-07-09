import {Format} from "../../Format.js";

export class ronKlaren extends Format
{
	name         = "Ron Klaren Module";
	website      = "http://fileformats.archiveteam.org/wiki/Ron_Klaren";
	ext          = [".rk"];
	magic        = ["Ron Klaren module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
