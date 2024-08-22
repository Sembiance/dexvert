import {Format} from "../../Format.js";

export class innoSetupArchive extends Format
{
	name           = "Inno Setup Archive";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = ["Inno Setup archive", "Inno Archiv gefunden"];
	unsupported    = true;
	notes          = "Could maybe write my own extractor, see sandbox/app/ednaunpack";
}
