import {Format} from "../../Format.js";

export class microsoftPublisher extends Format
{
	name           = "Microsoft Publisher Document";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Publisher";
	ext            = [".pub"];
	forbidExtMatch = true;
	magic          = ["Microsoft Publisher document", /^OLE 2 Compound Document.+Microsoft$/, /^OLE 2 Compound Document.+Microsoft Publisher$/, "Microsoft Publisher v1"];
	converters     = ["soffice"];
	notes          = "Older files like v1, v2, 95 and 98 don't convert. I tried installing Publisher 98 from WinWorld, and it couldn't open v1/v2/95. It could open 97, but it didn't allow you to save it as any other format. So meh.";
}
