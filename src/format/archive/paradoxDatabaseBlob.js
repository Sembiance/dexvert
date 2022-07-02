import {Format} from "../../Format.js";

export class paradoxDatabaseBlob extends Format
{
	name           = "Paradox Database Memo Field BLOB";
	website        = "http://fileformats.archiveteam.org/wiki/Paradox_(database)";
	ext            = [".mb"];
	forbidExtMatch = true;
	magic          = [/^x-fmt\/(307)( |$)/];
	notes          = "I tried using pxview to convert these, but it just segfaults, so fallback to foremost.";
	converters     = ["foremost"];
}
