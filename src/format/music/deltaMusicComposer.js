import {Format} from "../../Format.js";

export class deltaMusicComposer extends Format
{
	name         = "Delta Music Composer";
	website      = "http://justsolve.archiveteam.org/wiki/CMC";
	ext          = [".dlt"];
	magic        = ["Delta Music Composer"];
	metaProvider = ["musicInfo"];
	converters   = ["asapconv"];
}
