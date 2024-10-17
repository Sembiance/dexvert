import {Format} from "../../Format.js";

export class openOffice extends Format
{
	name           = "Open Office Document";
	website        = "http://fileformats.archiveteam.org/wiki/OpenOffice.org_XML";
	ext            = [".sxw", ".stw", ".stc", ".sti", ".sxc", ".sxi"];
	forbidExtMatch = true;
	magic          = [/^OpenOffice(\.org ) ?([\dx.]+ )?(Calc|Impress|Writer)/, "OpenOffice Impress presentation", "OpenOffice Calc spreadsheet", "application/vnd.sun.xml.writer", "application/vnd.sun.xml.impress", /^fmt\/(128|130|136|137)( |$)/];
	converters     = ["soffice[matchType:magic]"];
}
