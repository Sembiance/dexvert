import {Format} from "../../Format.js";

export class aixBackupRestore extends Format
{
	name           = "AIX/BFF backup/restore";
	ext            = [".bff", ".img"];
	forbidExtMatch = true;
	magic          = ["AIX backup/restore format file", "AIX Backup File Format", "Archive: BFF", "BFF volume header"];
	converters     = ["unAIXBFF"];
}
