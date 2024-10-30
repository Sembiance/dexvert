import {Format} from "../../Format.js";

export class openOffice extends Format
{
	name           = "Open Office Document";
	website        = "http://fileformats.archiveteam.org/wiki/OpenOffice.org_XML";
	ext            = [".sxw", ".stw", ".stc", ".sti", ".sxc", ".sxi", "sxd"];
	forbidExtMatch = true;
	magic          = [/^OpenOffice(\.org ) ?([\dx.]+ )?(Calc|Draw|Impress|Writer)/, "OpenOffice Impress presentation", "OpenOffice Calc spreadsheet", /^application\/vnd\.sun\.xml\.(calc|draw|impress|writer)/, /^fmt\/(127|128|130|136|137)( |$)/];
	converters     = ["soffice[matchType:magic]"];
}
