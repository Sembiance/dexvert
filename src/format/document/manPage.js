import {Format} from "../../Format.js";

export class manPage extends Format
{
	name           = "MAN Page";
	website        = "http://fileformats.archiveteam.org/wiki/Man_page";
	ext            = [".man", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8"];
	forbidExtMatch = true;
	magic          = ["Man page", "troff or preprocessor input", "TROFF markup", "text/troff"];
	converters     = ["man2html"];
}
