import {Format} from "../../Format.js";

export class sidMeiersFPK extends Format
{
	name           = "Sid Meiers FPK Archive";
	ext            = [".fpk"];
	forbidExtMatch = true;
	magic          = [/^geArchive: (FPK_FPK|FPK_FPK_2)( |$)/];	// , "dragon: FPK "  (see reason below commented out)
	converters     = [
		"gameextractor[codes:FPK_FPK_2,FPK_FPK]"
		//"dragonUnpacker[types:FPK4]"	// multi-versioned, so it detects as FPK but must pass like FPK4. This produces garbage though on non FPK4 archives. gameextractor handles these fine and much better, see sidMeiserFPK
	];
}
