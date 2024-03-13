import {Format} from "../../Format.js";

export class jeroenTel extends Format
{
	name         = "Jeroen Tel Module";
	website      = "http://fileformats.archiveteam.org/wiki/Jeroen_Tel";
	ext          = [".jt"];
	magic        = ["M.O.N Old / Jeroen Tel module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
