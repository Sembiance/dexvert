import {Format} from "../../Format.js";

const _MS_WORKS_DB_MAGIC = ["Microsoft Works for DOS DataBase", "Microsoft Works Database"];
export {_MS_WORKS_DB_MAGIC};

export class microsoftWorksDatabase extends Format
{
	name           = "Microsoft Works Database";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Works_Database";
	ext            = [".wdb"];
	forbidExtMatch = true;
	magic          = _MS_WORKS_DB_MAGIC;
	priority       = this.PRIORITY.LOW;
	converters     = ["strings"];
}
