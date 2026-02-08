import {Format} from "../../Format.js";

export class innoSetupArchive extends Format
{
	name           = "Inno Setup Archive";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = ["Inno Setup archive", "Inno Archiv gefunden", "Archive: Inno Setup"];
	unsupported    = true;	// handled by innoSetupInstaller
}
