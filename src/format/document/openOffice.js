import {Format} from "../../Format.js";

export class openOffice extends Format
{
	name           = "Open Office Document";
	website        = "http://fileformats.archiveteam.org/wiki/OpenOffice.org_XML";
	ext            = [".sxw", ".stw", ".stc", ".sti", ".sxc"];
	forbidExtMatch = true;
	magic          = [/^OpenOffice(\.org ) ?([\dx.]+ )?(Calc|Impress|Writer)/, /^fmt\/(128|130|136|137)( |$)/];
	converters     = ["soffice[matchType:magic]"];
}
