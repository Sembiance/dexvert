import {Format} from "../../Format.js";

export class greenstreetPublisher extends Format
{
	name           = "Greenstreet Publisher Document/Snippet";
	website        = "http://fileformats.archiveteam.org/wiki/Greenstreet_Publisher";
	ext            = [".dtp", ".srp"];
	forbidExtMatch = true;
	magic          = ["Greenstreet Publisher document", "Greenstreet Publisher snippet", /^fmt\/(1415|1416)( |$)/];
	notes          = "Some of these opened in Win2k with Publishing Suite 99, but it can't save in ANY other format, maybe I could 'print' to a PDF or something. But not all worked and not too many files out there, so not supported for now.";
	unsupported    = true;
}
