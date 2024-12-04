import {Format} from "../../Format.js";

export class appleSafariWebarchive extends Format
{
	name       = "Apple Safari Webarchive";
	website    = "http://fileformats.archiveteam.org/wiki/Webarchive_(Safari)";
	ext        = [".webarchive"];
	magic      = [/^Apple Safari Web[Aa]rchive$/, /^fmt\/866( |$)/];
	converters = ["pywebarchive"];
}
