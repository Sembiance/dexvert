import {Format} from "../../Format.js";

export class starWriter extends Format
{
	name           = "StarWriter Document";
	website        = "http://fileformats.archiveteam.org/wiki/SDW";
	ext            = [".sdw", ".tpl"];
	forbidExtMatch = true;
	magic          = ["StarOffice StarWriter document", "StarOffice Writer document", "StarWriter for MS-DOS document"];
	notes          = "Soffice doesn't support the older MS-DOS versions (.tpl files) but since I just fallback to strings, we allow it to convert to PDF because it basically does the same thing as strings in this case.";
	converters     = ["soffice", "strings"];
}
