import {Format} from "../../Format.js";

export class innoSetupArchive extends Format
{
	name           = "Inno Setup Archive";
	ext            = [".bin", ".0", ".1", ".2", ".3", ".4", ".5", ".6", ".7", ".8", ".9"];
	forbidExtMatch = true;
	magic          = ["Inno Setup archive", "Inno Archiv gefunden", "Archive: Inno Setup", "Inno Setup Setup Data", "My Inno Setup Extensions Data", "Inno Setup Data iPrefix"];
	unsupported    = true;	// handled by innoSetupInstaller
}
