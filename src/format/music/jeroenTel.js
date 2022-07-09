import {Format} from "../../Format.js";

export class jeroenTel extends Format
{
	name         = "Jeroen Tel Module";
	website      = "http://fileformats.archiveteam.org/wiki/Jeroen_Tel";
	ext          = [".jt"];
	magic        = ["M.O.N Old module"];	// Not sure why trid identifies them as this, but we'll take it :)
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
