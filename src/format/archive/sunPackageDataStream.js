import {Format} from "../../Format.js";

export class sunPackageDataStream extends Format
{
	name           = "Sun Package Data Stream";
	ext            = [".pkg"];
	forbidExtMatch = true;
	magic          = ["Sun SVR4 package data stream", "pkg Datastream"];
	converters     = ["sevenZip"];
}
