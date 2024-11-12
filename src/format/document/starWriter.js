import {Format} from "../../Format.js";

export class starWriter extends Format
{
	name           = "StarWriter Document";
	website        = "http://fileformats.archiveteam.org/wiki/SDW";
	ext            = [".sdw", ".tpl", ".vor"];
	forbidExtMatch = true;
	magic          = ["StarOffice StarWriter document", "StarOffice Writer document", "StarWriter for MS-DOS document", "StarWriter 2.x Document", "application/vnd.stardivision.writer", /^fmt\/(812|813)( |$)/, /^x-fmt\/400( |$)/];
	priority       = this.PRIORITY.LOW;
	notes          = "Soffice doesn't support the older MS-DOS versions (.tpl files) but since I just fallback to strings, we allow it to convert to PDF because it basically does the same thing as strings in this case.";
	converters     = ["soffice[format:StarOffice Writer]", "strings"];
}
