import {Format} from "../../Format.js";

export class microsoftWorksDatabase extends Format
{
	name           = "Microsoft Works Database";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Works_Database";
	ext            = [".wdb"];
	forbidExtMatch = true;
	magic          = ["Microsoft Works for DOS DataBase", "Microsoft Works Database"];
	priority       = this.PRIORITY.LOW;
	converters     = ["strings"];
}
